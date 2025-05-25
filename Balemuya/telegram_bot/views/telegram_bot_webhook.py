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

        # User lookup and state retrieval
        user = self.get_user(chat_id)
        user_state = cache.get(f'user_state_{chat_id}', None)

        # Create an instance of TelegramFacade
        facade = TelegramFacade(chat_id)

        # Check if user is logged in
        is_logged_in = user is not None
        facade.auth_service.set_session_data('is_logged_in', is_logged_in)

        # Call the handle_update method with the incoming data
        facade.handle_update(data)

        # Update user state in cache
        cache.set(f'user_state_{chat_id}', facade.auth_service.get_user_state())

        return JsonResponse({"status": "ok"})

    def get_user(self, chat_id):
        """Retrieve the user from the database based on chat_id."""
        try:
            return User.objects.get(telegram_chat_id=chat_id)
        except User.DoesNotExist:
            return None