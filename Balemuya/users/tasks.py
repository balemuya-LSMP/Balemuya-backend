# # users/tasks.py
# from celery import shared_task
# from django.utils import timezone
# from .models import SubscriptionPlan, Professional
# from django.core.mail import send_mail
# from django.conf import settings

# @shared_task
# def notify_expiring_subscriptions():
#     current_date = timezone.now()
#     expiration_threshold = current_date + timedelta(days=7)

#     expiring_subscriptions = SubscriptionPlan.objects.filter(
#         expiration_date__lte=expiration_threshold,
#         is_expired=False
#     )

#     for subscription in expiring_subscriptions:
#         try:
#             professional = Professional.objects.get(id=subscription.professional.id)
#             professional.is_available = False
#             professional.save()
#             send_notification_email(subscription.user.email)
#         except Professional.DoesNotExist:
#             continue

# @shared_task
# def send_notification_email(user_email):
#     if user_email:
#         send_mail(
#             'Your account subscription is expiring soon',
#             'Your subscription is expiring soon. Please renew it.',
#             settings.DEFAULT_FROM_EMAIL,
#             [user_email],
#             fail_silently=False,
#         )