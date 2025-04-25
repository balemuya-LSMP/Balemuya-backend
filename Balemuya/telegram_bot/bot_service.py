# telegram_bot/bot_service.py
from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings

def send_message_to_telegram(chat_id, message):
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        print(f"Error sending message: {e}")


# telegram_bot/bot_service.py
def set_webhook():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    webhook_url = "https://your-server-url/telegram/bot-webhook/"
    bot.setWebhook(url=webhook_url)
