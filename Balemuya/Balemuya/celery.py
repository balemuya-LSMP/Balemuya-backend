# # Balemuya/celery.py
# import os
# from celery import Celery

# # Set the default Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Balemuya.settings')

# # Create a Celery application instance
# app = Celery('Balemuya')

# app.config_from_object('django.conf:settings')

# # Specify the broker URL for Redis
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.autodiscover_tasks()