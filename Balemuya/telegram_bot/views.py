from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import requests
from django.conf import settings  # To get bot token from settings

class TelegramBotWebhook(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            message = data.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text")

            if text == "/start" and chat_id:
                self.send_message(chat_id, "Hello, user!")
            
            return JsonResponse({"status": "ok"})
        
        return JsonResponse({"status": "not allowed"}, status=405)

    def send_message(self, chat_id, text):
        bot_token = settings.TELEGRAM_BOT_TOKEN  # Make sure this is defined in your settings.py
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)
