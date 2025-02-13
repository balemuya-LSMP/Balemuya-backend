# users/scheduler.py
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
import json

def create_periodic_task():
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=30,  
        period=IntervalSchedule.SECONDS,
    )

    # Create or update the periodic task
    PeriodicTask.objects.update_or_create(
        interval=schedule,
        name='Notify Expiring Subscriptions',
        defaults={
            'task': 'users.tasks.notify_expiring_subscriptions',
            'args': json.dumps([]), 
            'enabled': True,
            'last_run_at': timezone.now(),  
        }
    )