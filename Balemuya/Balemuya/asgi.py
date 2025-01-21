"""
ASGI config for Balemuya project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from users import consumers 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Balemuya.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests (same as WSGI)

    # WebSocket routing for payment-related actions
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/initiate-payment/", consumers.PaymentInitiateConsumer.as_asgi()), 
            path("ws/confirm-payment/", consumers.PaymentConfirmConsumer.as_asgi()), 
        ])
    ),
})
