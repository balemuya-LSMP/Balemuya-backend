from django.urls import path, re_path, include
from .consumers import NotificationConsumer

websocket_urlpatterns= [
    re_path(r'ws/notifications/service-post/(?P<category>\w+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/application/(?P<customer_id>[0-9a-f-]+)/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/application-status/(?P<professional_id>[0-9a-f-]+)/$', NotificationConsumer.as_asgi()),
    ]