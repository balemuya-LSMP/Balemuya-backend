# views/telegram_bot_webhook.py

from rest_framework.views import APIView
from django.http import JsonResponse
from .services.telegram_facade import TelegramFacade
from django.core.cache import cache
import json

class TelegramBotWebhook(APIView):
    def post(self, request, *args, **kwargs):
        # Get data from the incoming Telegram request
        data = json.loads(request.body.decode('utf-8'))
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text")

        # Initialize the facade service for this chat
        facade = TelegramFacade(chat_id)

        # Get the current user state from the cache
        user_state = facade.auth_service.get_user_state()
        print(f"Received text: {text}")
        print(f"User state: {user_state}")

        # Start command - Main Menu
        if text == "/start":
            facade.auth_service.clear_session()  # Clear any existing session data
            facade.send_welcome_message()

        # Cancel operation - Reset session
        elif text == "/cancel" or text == "❌ Cancel":
            facade.auth_service.clear_session()
            facade.send_cancel_message()

        # Registration process - Asking for email
        elif text == "📝 Register":
            facade.ask_for_email()
            facade.auth_service.set_user_state("waiting_for_email")

        # Handling email entry in registration flow
        elif user_state == "waiting_for_email" and text:
            email = text.strip()
            if not facade.auth_service.validate_email(email):
                facade.bot_service.send_message(chat_id, "❌ Invalid email. Please try again.")
                return JsonResponse({"status": "ok"})  # Exit after invalid email

            # Store email in the cache
            facade.auth_service.set_session_data("email", email)
            facade.auth_service.set_user_state("waiting_for_password")
            facade.ask_for_password()
        # Handling email entry in registration flow
        elif user_state == "waiting_for_password" and text:
            password = text.strip()
            # Store email in the cache
            facade.auth_service.set_session_data("password", password)
            facade.auth_service.set_user_state("waiting_for_username")
            facade.ask_for_username()

        # Handling username entry
        elif user_state == "waiting_for_username" and text:
            facade.auth_service.set_session_data("username", text.strip())
            facade.auth_service.set_user_state("waiting_for_phone_number")
            facade.ask_for_phone_number()

        # Handling phone number entry
        elif user_state == "waiting_for_phone_number" and text:
            facade.auth_service.set_session_data("phone", text.strip())
            facade.auth_service.set_user_state("waiting_for_user_type")
            facade.ask_for_user_type()

        # Handling user type selection
        elif user_state == "waiting_for_user_type" and text in ["Customer", "Professional"]:
            facade.auth_service.set_session_data("user_type", text.strip().lower())
            facade.auth_service.set_user_state("waiting_for_entity_type")
            facade.ask_for_entity_type()

        # Handling entity type selection
        elif user_state == "waiting_for_entity_type" and text in ["Individual", "Organization"]:
            facade.auth_service.set_session_data("entity_type", text.strip().lower())

            # Prepare registration data from cache
            user_data = {
                "email": facade.auth_service.get_session_data("email"),
                "password": facade.auth_service.get_session_data("password"),
                "username": facade.auth_service.get_session_data("username"),
                "phone_number": facade.auth_service.get_session_data("phone"),
                "user_type": facade.auth_service.get_session_data("user_type"),
                "entity_type": facade.auth_service.get_session_data("entity_type"),
            }
            print('user data is ',user_data)

            response = facade.auth_service.send_registration_request(user_data)
            print('register call response is',response.get('status'))
            if response.get("status") == "success":
                print('success!!!!')
                facade.send_registration_success()
                facade.send_main_menu(message='Welcome back Now you can login!')
            else:
                facade.send_registration_failure()
                facade.send_main_menu()


            facade.auth_service.clear_session()  # Clear session after registration

        # Login process - Asking for email
        elif text == "🔐 Login":
            facade.ask_for_email()
            facade.auth_service.set_user_state("waiting_for_login_email")

        # Handling login email entry
        elif user_state == "waiting_for_login_email" and text:
            facade.auth_service.set_session_data("email", text.strip())
            facade.auth_service.set_user_state("waiting_for_login_password")
            facade.bot_service.send_message(chat_id, "🔑 Please provide your password:")

        # Handling password entry for login
        elif user_state == "waiting_for_login_password" and text:
            email = facade.auth_service.get_session_data("email")
            print('email is',email)
            password = text.strip()

            response = facade.auth_service.send_login_request(email, password)
            print('login call response is',response.get('status'))

            if response["status"] == "success":
                print('successful login send login success will be called')
                facade.send_login_success()
            else:
                facade.send_login_failure()

            facade.auth_service.clear_session()  # Clear session after login

        # Help command - Showing available options
        elif text == "ℹ️ Help":
            facade.send_help_message()

        return JsonResponse({"status": "ok"})
