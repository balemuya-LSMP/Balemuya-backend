from django.urls import path,re_path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    # path('ws/notifications/service-post/<str:category>/', NotificationConsumer.as_asgi()),
    # path('ws/notifications/application/<uuid:customer_id>/', NotificationConsumer.as_asgi()),
    # path('ws/notifications/application-status/<uuid:professional_id>/', NotificationConsumer.as_asgi()),
]
