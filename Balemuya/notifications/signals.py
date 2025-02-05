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
from .utils import get_professionals_in_proximity_and_category

User = get_user_model()


@receiver(post_save, sender=ServicePost)
def notify_professionals_about_new_post(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        message = f"New job posted: {instance.description[:50]}..."

        # Get professionals in proximity and category
        professionals = get_professionals_in_proximity_and_category(instance)

        # Notify each professional within proximity
        for professional in professionals:
            group_name = f"professional_{professional.user.id}_new_jobs"
            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'send_notification',
                'message': message
            })

        print(f"Notifications sent to professionals for job: {instance.description[:50]}...")

@receiver(post_save, sender=ServicePostApplication)
def notify_customer_about_application(sender, instance, created, **kwargs):
    if created:
        print('instance is ', instance)
        customer = instance.service.customer.user
        channel_layer = get_channel_layer()
        group_name = f"customer_{customer.id}_applications_requests"

        # The sender is the professional who applied
        notification_message = f"A professional has applied to your service post."
        notification = Notification.objects.create(
            sender=instance.professional.user,  
            message=notification_message,
            notification_type="application",  
            metadata={"name":"hay yike"},
            title='notification'
        )
        notification.recipient.set([customer])
        notification.save()
        print('i am called ')
        
        serializer = NotificationSerializer(notification)

        # Send serialized notification to the group
        async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'message': serializer.data 
                }
            )

        print('Notification sent to customer')
