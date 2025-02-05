# your_app/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import SubscriptionPlan
from django.core.mail import send_mail
from datetime import timedelta
from django.conf import settings

@shared_task
def notify_expiring_subscriptions():
    current_date = timezone.now().date()
    
    expiring_subscriptions = SubscriptionPlan.objects.filter(
        is_expired=True)

    for subscription in expiring_subscriptions:
        send_notification_email(subscription.user.email)

def send_notification_email(user_email):
    send_mail(
        'Your account subscription is getting to expired',
        'Your subscription is expiring soon. Please renew it.',
        settings.DEFAULT_FROM_EMAIL,  
        [user_email],
        fail_silently=False,
    )
    
    
@shared_task
def add(x, y):
    return x + y