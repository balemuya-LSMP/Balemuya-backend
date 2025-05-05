# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ServicePostReport
from django.conf import settings

@receiver(post_save, sender=ServicePostReport)
def auto_block_customer_if_reported_too_much(sender, instance, created, **kwargs):
    if not created:
        return
    
    service_post = instance.service_post
    customer = service_post.customer
    user = customer.user
    customer.report_count += 1
    customer.save()

    total_reports = customer.report_count 

    REPORT_THRESHOLD = 3  

    if total_reports >= REPORT_THRESHOLD and user.is_active and user.is_blocked == False:
        user.is_blocked = True
        user.save()
