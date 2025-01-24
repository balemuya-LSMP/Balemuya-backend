from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/<uuid:user_id>/', NotificationConsumer.as_asgi()),
    path('ws/notifications/service-post/<str:category>/', NotificationConsumer.as_asgi()),
    path('ws/notifications/application/<uuid:customer_id>/', NotificationConsumer.as_asgi()),
    path('ws/notifications/application-status/<uuid:professional_id>/', NotificationConsumer.as_asgi()),
]
