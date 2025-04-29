import os
import sys
import django
import requests

# 🔽 Add your project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🔽 Set your Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Balemuya.settings")
django.setup()

from django.conf import settings

# 🔽 Replace with your actual bot token and ngrok public URL
bot_token = settings.TELEGRAM_BOT_TOKEN
webhook_url = "https://b0e0-15-204-91-72.ngrok-free.app/api/telegram/webhook/"

url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
response = requests.get(url)

if response.status_code == 200:
    print("✅ Webhook set successfully!")
else:
    print("❌ Failed to set webhook:", response.text)
