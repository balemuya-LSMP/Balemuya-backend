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

        user = None
        try:
            user = User.objects.get(telegram_chat_id=chat_id)
        except User.DoesNotExist:
            self.handle_user_not_found(chat_id)
            return JsonResponse({"status": "user_not_found"}, status=404)

        # Get user state from cache
        user_state = cache.get(f'user_state_{chat_id}', None)
        print('Starting user state is', user_state)

        facade = TelegramFacade(chat_id)

        facade.auth_service.set_session_data('is_logged_in', True)

        facade.dispatch(text, user_state)

        cache.set(f'user_state_{chat_id}', facade.auth_service.get_user_state())

        return JsonResponse({"status": "ok"})

    def handle_user_not_found(self, chat_id):
        facade = TelegramFacade(chat_id)
        facade.bot_service.send_message(chat_id, "⚠️ User not found. Please login to continue.")