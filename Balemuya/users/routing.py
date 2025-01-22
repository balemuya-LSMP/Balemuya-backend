# # balemuya/routing.py
# from django.urls import re_path
# from users.consumers import InitiatePaymentConsumer

# websocket_urlpatterns = [
#     re_path(r"ws/payment/initiate/", InitiatePaymentConsumer.as_asgi()),
# ]

from django.urls import path
from users.consumers import InitiatePaymentConsumer

websocket_urlpatterns= [
        path('ws/payment/initiate/', InitiatePaymentConsumer.as_asgi()),
    ]

