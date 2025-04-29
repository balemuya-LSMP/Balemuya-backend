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
            callback_query = data.get("callback_query", {})
            chat_id = message.get("chat", {}).get("id") if message else callback_query.get("message", {}).get("chat", {}).get("id")
            text = message.get("text") if message else callback_query.get("data")

            # Handle the /start command and show the buttons
            if text == "/start" and chat_id:
                self.send_message_with_buttons(chat_id)

            # Handle button clicks (callback queries)
            elif callback_query:
                callback_data = callback_query.get("data")
                if callback_data == "option_1":
                    self.send_message(chat_id, "You selected Option 1!")
                elif callback_data == "option_2":
                    self.send_message(chat_id, "You selected Option 2!")
                elif callback_data == "option_3":
                    self.send_message(chat_id, "You selected Option 3!")

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

    def send_message_with_buttons(self, chat_id):
        # Creating inline buttons for the user
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Inline Keyboard with options
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Option 1", "callback_data": "option_1"},
                    {"text": "Option 2", "callback_data": "option_2"}
                ],
                [
                    {"text": "Option 3", "callback_data": "option_3"}
                ]
            ]
        }

        payload = {
            "chat_id": chat_id,
            "text": "Please choose an option:",
            "reply_markup": json.dumps(keyboard)
        }

        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)
