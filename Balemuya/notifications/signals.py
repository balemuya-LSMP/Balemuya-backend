from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from services.models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain
from .models import Notification
from users.models import Professional,Admin,Customer,User,VerificationRequest,Feedback
from common.models import Category
from .serializers import NotificationSerializer
from django.contrib.auth import get_user_model
from uuid import UUID
from .utils import get_professionals_in_proximity_and_category

User = get_user_model()


@receiver(post_save, sender=ServicePost)
def notify_professionals_about_new_post(sender, instance, created, **kwargs):
    if created:
        print('Post is created')
        channel_layer = get_channel_layer()
        message = f"New job posted: {instance.description[:50]}..."

        try:
            professionals = get_professionals_in_proximity_and_category(instance)

            if not professionals:
                print("No professionals found in proximity for this job.")
                return

            recipients = User.objects.filter(professional__in=professionals)

            if not recipients.exists():
                print("No users found for the professionals.")
                return

            with transaction.atomic():
                print("Creating notification...")
                
                notification = Notification.objects.create(
                    message=message,
                    metadata={
                        "job_id": str(instance.id),
                        "name": instance.customer.user.first_name,
                        "profile_image": instance.customer.user.profile_image.url if instance.customer.user.profile_image else None,
                        "email": instance.customer.user.email,
                        "id": str(instance.customer.user.id)  
                    },
                    notification_type="new_job",
                    title='New Job Post'
                )
                notification.recipient.set(recipients)
                notification_serializer = NotificationSerializer(notification)

            for professional in professionals:
                group_name = f"professional_{professional.user.id}_new_jobs"
                async_to_sync(channel_layer.group_add)(group_name, f"user_{professional.user.id}")

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'send_notification',
                        'data': notification_serializer.data
                    }
                )

            print(f"Notifications sent to professionals for job: {instance.description[:50]}...")

        except IntegrityError as e:
            print(f"Database error while creating notification: {e}")
        except ObjectDoesNotExist as e:
            print(f"Object not found error: {e}")
        except Exception as e:
            print(f"Unexpected error while sending notifications: {e}")

@receiver(post_save, sender=ServicePostApplication)
def notify_customer_about_application(sender, instance, created, **kwargs):
    if created:
        print('instance is ', instance)
        customer = instance.service.customer.user
        channel_layer = get_channel_layer()
        group_name = f"customer_{customer.id}_job_app_requests"

        # The sender is the professional who applied
        notification_message = f"A professional has applied to your service post {instance.service.title}..."
        notification = Notification.objects.create(
            message=notification_message,
            notification_type="job_apply",  
            metadata={"id":str(instance.professional.user.id),
                      "name":instance.professional.user.first_name,
                      "profile_image":instance.professional.user.profile_image.url if instance.professional.user.profile_image else None,
                      
            },
            title='job_apply'
        )
        notification.recipient.set([customer])
        notification.save()
        print('i am called ')
        
        serializer = NotificationSerializer(notification)

        async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'message': serializer.data 
                }
            )



@receiver(post_save, sender=VerificationRequest)
def send_verification_request_to_admin(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_verification_notifications"

        notification_message = f"A professional application request to verify!."
    
        notification = Notification.objects.create(
            message=notification_message,
            notification_type="verify_request",  
            metadata={"id":str(instance.professional.user.id),
                      "name":instance.professional.user.first_name,
                      "email":instance.professional.user.email,
                      "profile_image":instance.professional.user.profile_image.url if instance.professional.user.profile_image else None,},
            title='verification request'
        )
        recepients = User.objects.filter(user_type='admin')
        notification.recipient.set([recepients])
        notification.save()
        print('i am called ')
        
        serializer = NotificationSerializer(notification)

        async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'data': serializer.data 
                }
        )
        
        
@receiver(post_save, sender=VerificationRequest)
def notify_professional_on_verification(sender, instance, created, **kwargs):
    if not created:
        if instance.status in ['approved', 'rejected']:
            channel_layer = get_channel_layer()
            group_name = f"professional_{instance.professional.user.id}_ver_notifications"
            
            message = f"Your verification request has been {instance.status}."
            notification = Notification.objects.create(
                message=message,
                notification_type="verify_response",  
                title='verification response',
                metadata={
                    'id':instance.service.customer.id,
                    'name':instance.service.customer.user.first_name,
                    "email":instance.service.customer.user.email,
                    "profile_image":instance.service.customer.profile_image
                }
            )
            notification.recipient.set([instance.professional.user])
            notification.save()

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'data': message
                }
            )
            

@receiver(post_save, sender=ServiceBooking)
def notify_professional_on_service_booking(sender, instance, created, **kwargs):
    if created:
       
        if instance.status == 'pending':
            
            channel_layer = get_channel_layer()
            group_name = f"professional_{instance.application.professional.user.id}_new_bookings"
            message = f"A new booking has been made for your service post {instance.service_post.title}..."
            
            with transaction.atomic():
                notification = Notification.objects.create(
                    title='new booking',
                    message=message,
                    notification_type="new_booking",
                    metadata={"application_id":str(instance.application.id),
                            "post_title":instance.application.service_post.title,
                            "booking_status":instance.status,
                            "scheduled_date":instance.scheduled_date,
                            "name":instance.application.service.customer.user.first_name,
                            "profile_image":instance.application.service.customer.user.profile_image.url if instance.application.service.customer.user.profile_image else None,
                            "email":instance.application.service.customer.user.email,
                            "customer_id":str(instance.customer.user.id)}
                )
                
                notification.recipient.set([instance.application.professional.user])
                notification.save()
                
                notification_serializer = NotificationSerializer(notification)
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'send_notification',
                        'data': notification_serializer.data
                    }
                )
                
@receiver(post_save, sender=Complain)
def notify_admin_on_complain(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_booking_complaint_notifications"
        message = f"A new complain has been made for  service post {instance.booking.application.service.title}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='new complain',
                message=message,
                notification_type="new_complain",
                metadata={"complain_id":str(instance.id),
                        "booking_id":str(instance.booking.id),
                        "booking_status":instance.booking.status,
                        "name":instance.user.first_name,
                        "profile_image":instance.user.profile_image.url if instance.user.profile_image else None,
                        "complainant_id":str(instance.user.id),
                        "complainant_user_type":instance.user.user_type,
                        "booking_scheduled_date":instance.booking.scheduled_date.isoformat(),
                        "created_at":instance.created_at.isoformat()
                        }
            )
            recipient = User.objects.filter(user_type='admin')
            notification.recipient.set(recipient)
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'data': notification_serializer.data
                }
            )   
            
    

@receiver(post_save, sender=Feedback)
def notify_admins_on_feedback(sender,instance,created,**kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"admin_feedback_notifications"
        
        message = f"A new feedback has been made by {instance.user.first_name}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='new feedback',
                message=message,
                notification_type="new_feedback",
                metadata={"feedback_id":str(instance.id),
                        "user_id":str(instance.user.id),
                        "user_first_name":instance.user.first_name,
                        "user_profile_image":instance.user.profile_image.url if instance.user.profile_image else None,
                        "user_user_type":instance.user.user_type,
                        "created_at":instance.created_at
                        }
            )
            recipients = User.objects.filter(user_type='admin')
            notification.recipient.set([recipients])
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'data': notification_serializer.data
                }
            )   
            
            
@receiver(post_save, sender=Review)
def notify_user_on_review(sender, instance, created, **kwargs):
    if created:
        group_name = None
        channel_layer = get_channel_layer()
        
        if instance.user.user_type == 'customer':
            group_name = f"user_{instance.booking.application.professional.user.id}_review_notifications"
        elif instance.user.user_type == 'professional':
            group_name = f"user_{instance.booking.application.service.customer.user.id}_review_notifications"
        
        if group_name is None:
            return
        
        message = f"A new review has been made by {instance.user.first_name}..."
        
        with transaction.atomic():
            notification = Notification.objects.create(
                title='new review',
                message=message,
                notification_type="new_review",
                metadata={
                    "review_id": str(instance.id),
                    "user_id": str(instance.user.id),
                    "user_first_name": instance.user.first_name,
                    "user_profile_image": instance.user.profile_image.url if instance.user.profile_image else None,
                    "user_type": instance.user.user_type,
                    "created_at": instance.created_at.isoformat()  # Convert to string
                }
            )
            notification.recipient.set([instance.user])
            notification.save()
            
            notification_serializer = NotificationSerializer(notification)
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    "data": notification_serializer.data
                }
            )

                