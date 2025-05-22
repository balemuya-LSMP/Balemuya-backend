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
            pass
        
        print('user is',user)

        # Get user state from cache
        user_state = cache.get(f'user_state_{chat_id}', None)
        print('Starting user state is', user_state)

        facade = TelegramFacade(chat_id)
        user_type=None
        if facade.auth_service.user_instance:
            user_type=facade.auth_service.user_instance['user']['user_type']
        if user:
            facade.auth_service.set_session_data('is_logged_in', True)
        else:
            facade.auth_service.set_session_data('is_logged_in', False)


        facade.dispatch(text, user_state,user_type)

        cache.set(f'user_state_{chat_id}', facade.auth_service.get_user_state())

        return JsonResponse({"status": "ok"})

        