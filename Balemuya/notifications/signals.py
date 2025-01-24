from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from services.models import ServicePost, ServicePostApplication
from .models import Notification
from users.models import Professional
from common.models import Category
from .serializers import NotificationSerializer 
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=ServicePost)
def notify_professionals_about_new_post(sender, instance, created, **kwargs):
    if created:
        category = instance.category
        channel_layer = get_channel_layer()
        group_name = f"category_{category}"
        print('group name is',group_name)

        notification_message = f'A new service post has been created in the {category.name} category.'

        # Fetch professionals associated with the category
        professionals = Professional.objects.all()
        print('professionals',professionals)
        # Create notifications for each professional in the category
        for professional in professionals:
            notification = Notification.objects.create(
                recipient=professional.user,  # Set the recipient to the User
                sender=instance.customer.user,  # The customer who created the post
                message=notification_message
            )

            serializer = NotificationSerializer(notification)

            # Send serialized notification to the group
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'message': serializer.data
                }
            )

        print('Notifications sent to professionals')

@receiver(post_save, sender=ServicePostApplication)
def notify_customer_about_application(sender, instance, created, **kwargs):
    if created:
        customer = instance.customer  # The customer associated with the application
        channel_layer = get_channel_layer()
        group_name = f"customer_{customer.id}"

        # The sender is the professional who applied
        notification_message = f"A professional has applied to your service post."
        notification = Notification.objects.create(
            recipient=customer,  # The customer is the recipient
            sender=instance.professional.user,  # The professional who applied
            message=notification_message,
            application_id=instance.id  # Store the ID of the application
        )

        # Serialize the notification using the NotificationSerializer
        serializer = NotificationSerializer(notification)

        # Send serialized notification to the group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': serializer.data  # Use the serialized data
            }
        )

        print('Notification sent to customer')