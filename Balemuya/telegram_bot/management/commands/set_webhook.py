# your_project/management/commands/set_webhook.py
from django.core.management.base import BaseCommand
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Sets the webhook for the Telegram bot'

    def handle(self, *args, **kwargs):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        # webhook_url = "https://dark-cars-mix.loca.lt/api/telegram/webhook/"
        webhook_url = "https://balemuya-project.onrender.com/api/telegram/webhook/"

        url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
        response = requests.get(url)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("✅ Webhook set successfully!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Failed to set webhook: {response.text}"))
