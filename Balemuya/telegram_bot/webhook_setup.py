import requests
from django.conf import settings

bot_token = settings.TELEGRAM_BOT_TOKEN  # if stored in settings.py
webhook_url = "https://b0e0-15-204-91-72.ngrok-free.app/api/telegram/webhook/" 

url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
response = requests.get(url)

if response.status_code == 200:
    print("✅ Webhook set successfully!")
else:
    print("❌ Failed to set webhook:", response.text)
