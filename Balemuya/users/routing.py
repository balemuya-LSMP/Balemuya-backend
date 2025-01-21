from django.urls import path
from .consumers import PaymentInitiateConsumer,PaymentConfirmConsumer

websocket_urlpatterns = [
    path('ws/initiate-payment/',PaymentInitiateConsumer.as_asgi()),
    path("ws/confirm-payment/",PaymentConfirmConsumer.as_asgi()), 

]