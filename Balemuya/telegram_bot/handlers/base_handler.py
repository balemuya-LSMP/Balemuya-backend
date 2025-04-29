# handlers/base_handler.py

class BaseHandler:
    def __init__(self, bot_service, auth_service, chat_id, message):
        self.bot_service = bot_service
        self.auth_service = auth_service
        self.chat_id = chat_id
        self.message = message

    def store_tokens(self, access_token, refresh_token):
        self.auth_service.set_session_data("access_token", access_token)
        self.auth_service.set_session_data("refresh_token", refresh_token)

    def get_access_token(self):
        return self.auth_service.get_session_data("access_token")

    def get_refresh_token(self):
        return self.auth_service.get_session_data("refresh_token")
