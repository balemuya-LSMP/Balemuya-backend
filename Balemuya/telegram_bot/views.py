from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import requests
from django.conf import settings

class TelegramBotWebhook(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            message = data.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text")

            if text == "/start" and chat_id:
                self.send_message(chat_id, "Welcome! Are you a Customer or a Professional?")
                self.send_buttons(chat_id, ["I am a Customer", "I am a Professional"])

            elif text == "I am a Customer" and chat_id:
                self.send_message(chat_id, "Great! How can we assist you today?")
                self.send_buttons(chat_id, ["Post a Service Request", "View Active Requests", "Cancel Request"])

            elif text == "I am a Professional" and chat_id:
                self.send_message(chat_id, "Great! What would you like to do?")
                self.send_buttons(chat_id, ["View New Job Requests", "View My Applications"])

            elif text == "Post a Service Request" and chat_id:
                self.send_message(chat_id, "Please provide a description of the service you need.")
                # Implement service posting logic here
                self.send_message(chat_id, "Your service has been posted successfully.")

            elif text == "View Active Requests" and chat_id:
                # Fetch active requests and display them
                self.send_message(chat_id, "Here are the active service requests.")
                # Implement logic to show requests here

            elif text == "Apply for Job" and chat_id:
                self.send_message(chat_id, "You have applied for this job!")
                # Implement job application logic here

            elif text == "Accept Application" and chat_id:
                self.send_message(chat_id, "You have accepted the application.")
                # Implement application acceptance logic here

            elif text == "Reject Application" and chat_id:
                self.send_message(chat_id, "You have rejected the application.")
                # Implement application rejection logic here

            elif text == "Pay via App" and chat_id:
                self.send_message(chat_id, "Proceeding with app payment.")
                # Implement payment logic here

            elif text == "Pay in Cash" and chat_id:
                self.send_message(chat_id, "You chose to pay in cash.")
                # Implement cash payment confirmation here

            return JsonResponse({"status": "ok"})

        return JsonResponse({"status": "not allowed"}, status=405)

    def send_message(self, chat_id, text):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)

    def send_buttons(self, chat_id, options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        buttons = [{"text": option} for option in options]
        payload = {
            "chat_id": chat_id,
            "text": "Please choose an option:",
            "reply_markup": {
                "keyboard": [buttons],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
        }
        headers = {"Content-Type": "application/json"}
        requests.post(url, json=payload, headers=headers)
