from django.urls import re_path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/service-post/(?P<category>\w+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/application/(?P<customer_id>[0-9a-f-]+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/application-status/(?P<professional_id>[0-9a-f-]+)/$', NotificationConsumer.as_asgi()),
]
