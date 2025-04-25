# telegram_bot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.TelegramBotWebhook.as_view(), name='send-message'),
    # path('bot-webhook/', views.bot_webhook, name='bot-webhook'),

]
