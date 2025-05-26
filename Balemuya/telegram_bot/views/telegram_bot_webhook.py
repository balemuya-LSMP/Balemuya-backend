from rest_framework.views import APIView
from django.http import JsonResponse
from ..services.telegram_facade import TelegramFacade
import json
from django.core.cache import cache
from users.models import User

class TelegramBotWebhook(APIView):
    def post(self, request, *args, **kwargs):
        # Parse the incoming update from Telegram
        data = json.loads(request.body.decode('utf-8'))
        
        # Extract chat_id from either message or callback_query
        chat_id = data.get("message", {}).get("chat", {}).get("id") or data.get("callback_query", {}).get("from", {}).get("id")

        user = self.get_user(chat_id)
        print('user is',user)
        user_state = cache.get(f'user_state_{chat_id}', None)

        facade = TelegramFacade(chat_id)

        is_logged_in = user is not None
        facade.auth_service.set_session_data('is_logged_in', is_logged_in)

        facade.handle_update(data)

        # Update user state in cache
        cache.set(f'user_state_{chat_id}', facade.auth_service.get_user_state())

        return JsonResponse({"status": "ok"})

    def get_user(self, chat_id):
        try:
            return User.objects.filter(telegram_chat_id=chat_id).first()
        except User.DoesNotExist:
            return None