# telegram_bot/urls.py
from django.urls import path
from .views.telegram_bot_webhook  import TelegramBotWebhook

urlpatterns = [
    path('webhook/', TelegramBotWebhook.as_view(), name='send-message'),

]
