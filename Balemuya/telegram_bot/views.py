from rest_framework.views import APIView
from django.http import JsonResponse
from .services import TelegramAuthService, TelegramBotService
from .utils import generate_keyboard
from django.conf import settings
import json

class TelegramBotWebhook(APIView):

    def post(self, request, *args, **kwargs):
        # Get data from the incoming Telegram request
        data = json.loads(request.body.decode('utf-8'))
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text")

        # Initialize bot service and authentication service
        bot_service = TelegramBotService(settings.TELEGRAM_BOT_TOKEN)
        auth_service = TelegramAuthService(chat_id)

        # Get the current user state from the session
        user_state = auth_service.get_user_state()
        print(f"Received text: {text}")
        print(f"User state: {user_state}")

        # Start command - Main Menu
        if text == "/start":
            auth_service.clear_session()  # Clear any existing session data
            bot_service.send_message(
                chat_id,
                "👋 Welcome to Balemuya!\nPlease choose an option:",
                reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help", "❌ Cancel"]])
            )

        # Cancel operation - Reset session
        elif text == "/cancel" or text == "❌ Cancel":
            auth_service.clear_session()
            bot_service.send_message(
                chat_id,
                "🚫 Operation cancelled. You're back to the main menu.",
                reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help"]])
            )

        # Registration process - Asking for email
        elif text == "📝 Register":
            bot_service.send_message(chat_id, "📧 Please provide your email address:")
            auth_service.set_user_state("waiting_for_email")

        # Handling email entry in registration flow
        elif user_state == "waiting_for_email" and text:
            email = text.strip()
            if not auth_service.validate_email(email):
                bot_service.send_message(chat_id, "❌ Invalid email. Please try again.")
                return JsonResponse({"status": "ok"})  # Exit after invalid email

            # Store email in the session
            request.session['email'] = email
            auth_service.set_user_state("waiting_for_username")
            bot_service.send_message(chat_id, "👤 Please provide your username:")

        # Handling username entry
        elif user_state == "waiting_for_username" and text:
            request.session['username'] = text.strip()
            auth_service.set_user_state("waiting_for_phone_number")
            bot_service.send_message(chat_id, "📱 Please provide your phone number:")

        # Handling phone number entry
        elif user_state == "waiting_for_phone_number" and text:
            request.session['phone'] = text.strip()
            auth_service.set_user_state("waiting_for_user_type")
            bot_service.send_message(
                chat_id,
                "🧑‍💼 Choose user type:",
                reply_markup=generate_keyboard([["Customer", "Professional"]])
            )

        # Handling user type selection
        elif user_state == "waiting_for_user_type" and text in ["Customer", "Professional"]:
            request.session['user_type'] = text.strip()
            auth_service.set_user_state("waiting_for_entity_type")
            bot_service.send_message(
                chat_id,
                "🏢 Choose entity type:",
                reply_markup=generate_keyboard([["Individual", "Business"]])
            )

        # Handling entity type selection
        elif user_state == "waiting_for_entity_type" and text in ["Individual", "Business"]:
            request.session['entity_type'] = text.strip()

            # Prepare registration data
            user_data = {
                "email": request.session.get('email'),
                "username": request.session.get('username'),
                "phone_number": request.session.get('phone'),
                "user_type": request.session.get('user_type'),
                "entity_type": request.session.get('entity_type'),
            }

            response = auth_service.send_registration_request(user_data)

            if response.get("status") == "success":
                bot_service.send_message(chat_id, "✅ Registration successful! Please verify your email.")
            else:
                bot_service.send_message(chat_id, "❌ Registration failed. Please try again.")

            auth_service.clear_session()  # Clear session after registration

        # Login process - Asking for email
        elif text == "🔐 Login":
            bot_service.send_message(chat_id, "📧 Please provide your email:")
            auth_service.set_user_state("waiting_for_login_email")

        # Handling login email entry
        elif user_state == "waiting_for_login_email" and text:
            request.session['email'] = text.strip()
            auth_service.set_user_state("waiting_for_login_password")
            bot_service.send_message(chat_id, "🔑 Please provide your password:")

        # Handling password entry for login
        elif user_state == "waiting_for_login_password" and text:
            email = request.session.get('email')
            password = text.strip()
            
            print('payload datas for login is','email:',email,'password',password)

            response = auth_service.send_login_request(email, password)

            if response["status"] == "success":
                bot_service.send_message(chat_id, "🎉 Login successful!")
            else:
                bot_service.send_message(chat_id, "❌ Login failed. Check your credentials.")

            auth_service.clear_session()  # Clear session after login

        # Help command - Showing available options
        elif text == "ℹ️ Help":
            bot_service.send_message(
                chat_id,
                "ℹ️ You can use the following options:\n"
                "- 📝 Register: Create a new account\n"
                "- 🔐 Login: Access your existing account\n"
                "- ❌ Cancel: Cancel the current operation"
            )

        return JsonResponse({"status": "ok"})
