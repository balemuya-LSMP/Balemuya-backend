# services/handlers/registration_handler.py

class RegistrationHandler:
    def __init__(self, facade):
        self.facade = facade

    def handle(self, text, user_state):
        chat_id = self.facade.chat_id
        auth = self.facade.auth_service
        bot = self.facade.bot_service

        if text == "📝 Register":
            self.facade.ask_for_email()
            auth.set_user_state("waiting_for_register_email")

        elif user_state == "waiting_for_register_email":
            if not auth.validate_email(text):
                bot.send_message(chat_id, "❌ Invalid email. Try again:")
                return
            auth.set_session_data("email", text.strip())
            auth.set_user_state("waiting_for_register_password")
            self.facade.ask_for_password()

        elif user_state == "waiting_for_register_password":
            auth.set_session_data("password", text.strip())
            auth.set_user_state("waiting_for_register_username")
            self.facade.ask_for_username()

        elif user_state == "waiting_for_register_username":
            auth.set_session_data("username", text.strip())
            auth.set_user_state("waiting_for_register_phone_number")
            self.facade.ask_for_phone_number()

        elif user_state == "waiting_for_register_phone_number":
            auth.set_session_data("phone", text.strip())
            auth.set_user_state("waiting_for_register_user_type")
            self.facade.ask_for_user_type()

        elif user_state == "waiting_for_register_user_type" and text in ["Customer", "Professional"]:
            auth.set_session_data("user_type", text.strip().lower())
            auth.set_user_state("waiting_for_register_entity_type")
            self.facade.ask_for_entity_type()

        elif user_state == "waiting_for_register_entity_type" and text in ["Individual", "Organization"]:
            auth.set_session_data("entity_type", text.strip().lower())

            user_data = {
                "email": auth.get_session_data("email"),
                "password": auth.get_session_data("password"),
                "username": auth.get_session_data("username"),
                "phone_number": auth.get_session_data("phone"),
                "user_type": auth.get_session_data("user_type"),
                "entity_type": auth.get_session_data("entity_type"),
            }

            response = auth.send_registration_request(user_data)

            if response.get("status") == "success":
                self.facade.send_registration_success()
                self.facade.send_main_menu("✅ Registered! You can now log in.")
            else:
                self.facade.send_registration_failure()
                self.facade.send_main_menu("❌ Registration failed. Try again.")

            auth.clear_session()
