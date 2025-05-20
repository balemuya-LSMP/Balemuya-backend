from rest_framework.views import APIView
from django.http import JsonResponse
from ..services.telegram_facade import TelegramFacade
import json
from django.core.cache import cache

from users.models import User


class TelegramBotWebhook(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text")

        facade = TelegramFacade(chat_id)

        facade.dispatch(text, user_state)

        cache.set(f'user_state_{chat_id}', facade.auth_service.get_user_state())

        return JsonResponse({"status": "ok"})