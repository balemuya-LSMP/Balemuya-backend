# handlers/bot_command_handler.py

class BotCommandHandler:
    def __init__(self, bot_service, auth_service, message, chat_id):
        self.bot_service = bot_service
        self.auth_service = auth_service
        self.message = message
        self.chat_id = chat_id
        self.state = auth_service.get_user_state()

    def handle(self):
        # First check static commands like /start, /cancel
        if self.message == "/start":
            return StartHandler(self).handle()
        elif self.message == "/cancel" or self.message == "❌ Cancel":
            return CancelHandler(self).handle()
        elif self.message == "📝 Register":
            return RegisterInitiateHandler(self).handle()
        elif self.message == "🔐 Login":
            return LoginInitiateHandler(self).handle()
        elif self.message == "ℹ️ Help":
            return HelpHandler(self).handle()

        # Then state-driven flow
        state_map = {
            "waiting_for_email": RegisterEmailHandler,
            "waiting_for_username": RegisterUsernameHandler,
            "waiting_for_phone_number": RegisterPhoneHandler,
            "waiting_for_user_type": RegisterUserTypeHandler,
            "waiting_for_entity_type": RegisterEntityTypeHandler,
            "waiting_for_login_email": LoginEmailHandler,
            "waiting_for_login_password": LoginPasswordHandler,
        }

        if self.state in state_map:
            return state_map[self.state](self).handle()

        return {"status": "ok"} 
