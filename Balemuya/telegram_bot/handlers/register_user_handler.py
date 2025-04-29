# handlers/register_user_handler.py

from .base_handler import BaseHandler

class RegisterUserHandler(BaseHandler):
    def handle(self):
        user_state = self.auth_service.get_user_state()
        message = self.message.strip()

        if user_state == "waiting_for_email":
            if not self.auth_service.validate_email(message):
                self.bot_service.send_message(self.chat_id, "❌ Invalid email. Please try again.")
                return {"status": "ok"}
            self.auth_service.set_session_data("email", message)
            self.auth_service.set_user_state("waiting_for_username")
            self.bot_service.send_message(self.chat_id, "👤 Please provide your username:")

        elif user_state == "waiting_for_username":
            self.auth_service.set_session_data("username", message)
            self.auth_service.set_user_state("waiting_for_phone_number")
            self.bot_service.send_message(self.chat_id, "📱 Please provide your phone number:")

        elif user_state == "waiting_for_phone_number":
            self.auth_service.set_session_data("phone", message)
            self.auth_service.set_user_state("waiting_for_user_type")
            self.bot_service.send_message(
                self.chat_id,
                "🧑‍💼 Choose user type:",
                reply_markup=self.generate_keyboard([["Customer", "Professional"]])
            )

        elif user_state == "waiting_for_user_type" and message in ["Customer", "Professional"]:
            self.auth_service.set_session_data("user_type", message)
            self.auth_service.set_user_state("waiting_for_entity_type")
            self.bot_service.send_message(
                self.chat_id,
                "🏢 Choose entity type:",
                reply_markup=self.generate_keyboard([["Individual", "Organization"]])
            )

        elif user_state == "waiting_for_entity_type" and message in ["Individual", "Organization"]:
            self.auth_service.set_session_data("entity_type", message)

            user_data = {
                "email": self.auth_service.get_session_data("email"),
                "username": self.auth_service.get_session_data("username"),
                "phone_number": self.auth_service.get_session_data("phone"),
                "user_type": self.auth_service.get_session_data("user_type"),
                "entity_type": self.auth_service.get_session_data("entity_type"),
            }

            response = self.auth_service.send_registration_request(user_data)

            if response.get("status") == "success":
                self.bot_service.send_message(self.chat_id, "✅ Registration successful! Please verify your email.")
            else:
                self.bot_service.send_message(self.chat_id, "❌ Registration failed. Please try again.")

            self.auth_service.clear_session()

        else:
            self.bot_service.send_message(self.chat_id, "❓ Unrecognized input. Please follow the registration steps.")
        
        return {"status": "ok"}

    def generate_keyboard(self, options):
        return self.bot_service.generate_keyboard(options)
