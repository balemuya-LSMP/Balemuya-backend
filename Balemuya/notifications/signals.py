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
from uuid import UUID

User = get_user_model()

@receiver(post_save, sender=ServicePost)
def notify_professionals_about_new_post(sender, instance, created, **kwargs):
     if created:
        category = instance.category
        channel_layer = get_channel_layer()
        group_name = f"category_{category.name}"  # Use category ID to identify the group
        print('group name is', group_name)

        notification_message = f'A new service post has been created in the {category.name} category.'
        
        print('category is',category)
        # Fetch professionals associated with the category (many-to-many relationship)
        professionals = Professional.objects.filter(categories=category.id)
        print('professionals:', professionals)

        recipients = []
        for professional in professionals:
            recipients.append(professional.user)

        # Create the notification (sending it to all recipients)
        notification = Notification.objects.create(
            sender=instance.customer.user,
            message=notification_message,
            notification_type="service_post",
        )
        # Set the recipients for the notification
        notification.recipient.set(recipients)
        notification.save()

        # Serialize the notification using the NotificationSerializer
        serializer = NotificationSerializer(notification)
        notification_data = serializer.data
        print('notification data',notification_data)
        # Send serialized notification to the group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': notification_data
            }
        )

        print('Notifications sent to professionals')

@receiver(post_save, sender=ServicePostApplication)
def notify_customer_about_application(sender, instance, created, **kwargs):
    if created:
        customer = instance.customer  # The customer associated with the application
        channel_layer = get_channel_layer()
        group_name = f"customer_{customer.id}"  # Group name based on customer ID

        # The sender is the professional who applied
        notification_message = f"A professional has applied to your service post."
        notification = Notification.objects.create(
            recipient=customer,  # The customer is the recipient
            sender=instance.professional.user,  # The professional who applied
            message=notification_message,
            notification_type="application",  # Add the notification type
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
