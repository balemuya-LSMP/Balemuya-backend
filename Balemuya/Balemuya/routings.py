from django.urls import path
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
from services.routing import websocket_urlpatterns as services_websocket_urlpatterns

# Combine both WebSocket URL patterns
websocket_urlpatterns = (
    notifications_websocket_urlpatterns +
    services_websocket_urlpatterns
)