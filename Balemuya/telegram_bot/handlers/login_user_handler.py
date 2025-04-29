# handlers/login_user_handler.py

from .base_handler import BaseHandler

class LoginUserHandler(BaseHandler):
    def handle(self):
        user_state = self.auth_service.get_user_state()
        message = self.message.strip()

        if user_state == "waiting_for_login_email":
            if not self.auth_service.validate_email(message):
                self.bot_service.send_message(self.chat_id, "❌ Invalid email. Please try again.")
                return {"status": "ok"}

            self.auth_service.set_session_data("email", message)
            self.auth_service.set_user_state("waiting_for_login_password")
            self.bot_service.send_message(self.chat_id, "🔑 Please provide your password:")

        elif user_state == "waiting_for_login_password":
            email = self.auth_service.get_session_data("email")
            password = message

            response = self.auth_service.send_login_request(email, password)

            if response.get("status") == "success":
                access = response.get("access")
                refresh = response.get("refresh")

                self.store_tokens(access, refresh)
                self.bot_service.send_message(self.chat_id, "🎉 Login successful!")

            else:
                self.bot_service.send_message(self.chat_id, "❌ Login failed. Check your credentials.")

            self.auth_service.clear_session()

        else:
            self.bot_service.send_message(self.chat_id, "❓ Please initiate login by selecting 🔐 Login.")
        
        return {"status": "ok"}
