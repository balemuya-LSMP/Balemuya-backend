# telegram_bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import json
import requests


class TelegramBotWebhook(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return JsonResponse({"status": "failure"}, status=400)

        try:
            data = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JsonResponse({"status": "invalid JSON"}, status=400)

        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if chat_id:
            if text == "/start":
                self.send_message(chat_id, "👋 Welcome to Balemuya Bot! How can I assist you today?")
            else:
                self.send_message(chat_id, "🤖 I'm here to help you with your service bookings!")
            return JsonResponse({"status": "success"}, status=200)

        return JsonResponse({"status": "no chat_id found"}, status=400)

    def send_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        return response
