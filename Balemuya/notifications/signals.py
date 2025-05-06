from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from services.models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain,ServiceRequest
from .models import Notification
from users.models import Professional,Customer,Admin,User,VerificationRequest,Feedback
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

        try:
            professionals = get_professionals_in_proximity_and_category(instance)

            if not professionals:
                return

            recipients = User.objects.filter(professional__in=professionals)

            if not recipients.exists():
                return
            
            
            with transaction.atomic():
                notification = Notification.objects.create(
                    message=message,
                    metadata={
                        "id": str(instance.user.id),
                        "username": instance.customer.username,
                        "profile_image": str(instance.customer.profile_image.url) or  None,
                    },
                    notification_type="new_job",
                    title='New Job Posted'
                )
                notification.recipient.set(recipients)
                notification_serializer = NotificationSerializer(notification)

            for professional in professionals:
                group_name = f"professional_{professional.user.id}_new_jobs"
                async_to_sync(channel_layer.group_add)(group_name, f"user_{professional.user.id}")
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {'type': 'send_notification', 'data': notification_serializer.data}
                )

        except IntegrityError as e:
            print(f"Database error while creating notification: {e}")
        except ObjectDoesNotExist as e:
            print(f"Object not found error: {e}")
        except Exception as e:
            print(f"Unexpected error while sending notifications: {e}")

@receiver(post_save, sender=ServicePostApplication)
def notify_customer_about_application(sender, instance, created, **kwargs):
    if created:
        customer = instance.service.customer.user
        channel_layer = get_channel_layer()
        group_name = f"customer_{customer.id}_job_app_requests"

        notification_message = f"A professional has applied to your service post {instance.service.title}..."
        notification = Notification.objects.create(
            message=notification_message,
            notification_type="job_apply",  
            metadata={
                "id": str(instance.professional.user.id),
                "username": instance.professional.user.username,
                "profile_image": str(instance.professional.user.profile_image.url) or None,
            },
            title='Job Application Received'
        )
        notification.recipient.set([customer])
        notification.save()

        serializer = NotificationSerializer(notification)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {'type': 'send_notification', 'message': serializer.data}
        )

@receiver(post_save, sender=VerificationRequest)
def send_verification_request_to_admin(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_verification_notifications"

        notification_message = f"A professional application request to verify."
        notification = Notification.objects.create(
            message=notification_message,
            notification_type="verify_request",  
            metadata={
                "id": str(instance.professional.user.id),
                "username": instance.professional.user.username,
                "profile_image": str(instance.professional.user.profile_image.url) or None,
            },
            title='Verification Request Submitted'
        )
        recipients = User.objects.filter(user_type='admin')
        notification.recipient.set(recipients)
        notification.save()

        serializer = NotificationSerializer(notification)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {'type': 'send_notification', 'data': serializer.data}
        )

@receiver(post_save, sender=VerificationRequest)
def notify_professional_on_verification(sender, instance, created, **kwargs):
    if not created and instance.status in ['approved', 'rejected']:
        channel_layer = get_channel_layer()
        group_name = f"professional_{instance.professional.user.id}_ver_notifications"
        
        message = f"Your verification request has been {instance.status}."
        notification = Notification.objects.create(
            message=message,
            notification_type="verify_response",  
            title='Verification Response from admin',
            metadata={
                'id': str(instance.professional.user.id),
                'username': instance.professional.user.username,
                'profile_image': str(instance.professional.user.profile_image.url) or None
            }
        )
        notification.recipient.set([instance.professional.user])
        notification.save()

        async_to_sync(channel_layer.group_send)(
            group_name,
            {'type': 'send_notification', 'data': message}
        )

@receiver(post_save, sender=ServiceBooking)
def notify_professional_on_service_booking(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        channel_layer = get_channel_layer()
        group_name = f"professional_{instance.application.professional.user.id}_new_bookings"
        message = f"A new booking has been made for your service post {instance.application.service.title}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='New Booking Notification',
                message=message,
                notification_type="new_booking",
                metadata={
                    "id": str(instance.application.service.customer.user.id),
                    "username": instance.application.service.customer.user.username,
                    "profile_image": str(instance.application.service.customer.user.profile_image.url) or None,
                }
            )
            notification.recipient.set([instance.application.professional.user])
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )

@receiver(post_save, sender=ServiceRequest)
def notify_professional_on_service_request(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        channel_layer = get_channel_layer()
        group_name = f"professional_{instance.professional.user.id}_new_job_request"
        message = f"A new job request from {instance.customer.user.username}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='New Job Request',
                message=message,
                notification_type="new_job_request",
                metadata={
                    "id": str(instance.customer.id),
                    "username": instance.customer.user.username,
                    "profile_image": str(instance.customer.user.profile_image.url) or None,
                }
            )
            notification.recipient.set([instance.professional.user])
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )

@receiver(post_save, sender=ServiceRequest)
def notify_customer_on_service_response(sender, instance, created, **kwargs):
    if not created and instance.status != 'pending':
        channel_layer = get_channel_layer()
        group_name = f"customer_{instance.customer.user.id}_job_request_response"
        message = f"{instance.professional.user.username} has {instance.status} your request."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='Job Request Response',
                message=message,
                notification_type="new_job_response",
                metadata={
                    "id": str(instance.professional.id),
                    "username": instance.professional.username,
                    "profile_image": str(instance.professional.user.profile_image.url)or None,
                }
            )
            notification.recipient.set(instance.customer.user)
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )

@receiver(post_save, sender=Complain)
def notify_admin_on_complain(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_booking_complaint_notifications"
        
        message = None
        if instance.booking:
            message = f"A new complaint has been made for service post {instance.booking.application.service.title}..."
        elif instance.service_request:
            message = f"A new complaint has been made for service request job."

        with transaction.atomic():
            notification = Notification.objects.create(
                title='New Complaint',
                message=message,
                notification_type="new_complain",
                metadata={
                    "id": str(instance.user.id),
                    "username": instance.user.username,
                    "profile_image": str(instance.user.profile_image.url)or None,
                }
            )
            recipients = User.objects.filter(user_type='admin')
            notification.recipient.set(recipients)
            notification.save()

            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )

@receiver(post_save, sender=Feedback)
def notify_admins_on_feedback(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_feedback_notifications"
        
        message = f"A new feedback has been made by {instance.user.username}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='New Feedback',
                message=message,
                notification_type="new_feedback",
                metadata={
                    "id": str(instance.user.id),
                    "username": instance.user.username,
                    "profile_image": str(instance.user.profile_image.url)or None,
                }
            )
            recipients = User.objects.filter(user_type='admin')
            notification.recipient.set(recipients)
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )

@receiver(post_save, sender=Review)
def notify_user_on_review(sender, instance, created, **kwargs):
    if created:
        group_name = None
        channel_layer = get_channel_layer()
        
        if instance.user.user_type == 'customer':
            if instance.booking:
                group_name = f"user_{instance.booking.application.professional.user.id}_review_notifications"
            else:
                group_name = f"user_{instance.service_request.professional.user.id}_review_notifications"

        elif instance.user.user_type == 'professional':
            if instance.booking:
                group_name = f"user_{instance.booking.application.service.customer.user.id}_review_notifications"
            else:
                group_name = f"user_{instance.service_request.customer.user.id}_review_notifications"

        
        if group_name is None:
            return
        
        message = f"A new review has been made by {instance.user.username}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='New Review',
                message=message,
                notification_type="new_review",
                metadata={
                    "id": str(instance.user.id),
                    "username": instance.user.username,
                    "profile_image": str(instance.user.profile_image.url) or None,
                }
            )
            notification.recipient.set([instance.user])
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {'type': 'send_notification', 'data': notification_serializer.data}
            )