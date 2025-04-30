# bot_services/telegram_facade.py

from .bot_services import TelegramBotService
from .bot_services import TelegramAuthService
from ..utils import generate_keyboard
from .handlers.registration_handler import RegistrationHandler
from .handlers.login_handler import LoginHandler
from django.conf import settings

class TelegramFacade:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.bot_service = TelegramBotService(settings.TELEGRAM_BOT_TOKEN)
        self.auth_service = TelegramAuthService(chat_id)
        self.registration_handler = RegistrationHandler(self)
        self.login_handler = LoginHandler(self)

    def send_main_menu(self, message="Please choose an option:"):
        self.bot_service.send_message(
            self.chat_id,
            message,
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help", "❌ Cancel"]])
        )

    def send_welcome_message(self):
        self.send_main_menu("👋 Welcome to Balemuya!\nPlease choose an option:")

    def send_cancel_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "🚫 Operation cancelled. You're back to the main menu.",
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help"]])
        )

    def send_help_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "ℹ️ You can use the following options:\n"
            "- 📝 Register: Create a new account\n"
            "- 🔐 Login: Access your existing account\n"
            "- ❌ Cancel: Cancel the current operation"
        )

    def dispatch(self, text, user_state):
        """Route to the correct handler based on user state or command"""
        if text == "/start":
            self.auth_service.clear_session()
            self.send_welcome_message()
        elif text in ["/cancel", "❌ Cancel"]:
            self.auth_service.clear_session()
            self.send_cancel_message()
        elif text == "ℹ️ Help":
            self.send_help_message()
        elif text == "📝 Register" or (user_state and user_state.startswith("waiting_for_") and "register" in user_state):
            self.registration_handler.handle(text, user_state)
        elif text == "🔐 Login" or (user_state and user_state.startswith("waiting_for_") and "login" in user_state):
            self.login_handler.handle(text, user_state)
        else:
            self.send_main_menu("⚠️ Unknown command. Please select an option.")


    def send_main_menu(self,message):
        self.bot_service.send_message(
            self.chat_id,
           message,
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help", "❌ Cancel"]])
        )
    def send_welcome_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "👋 Welcome to Balemuya!\nPlease choose an option:",
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help", "❌ Cancel"]])
        )

    def send_cancel_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "🚫 Operation cancelled. You're back to the main menu.",
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help"]])
        )

    def ask_for_email(self):
        self.bot_service.send_message(self.chat_id, "📧 Please provide your email address:")

    def ask_for_password(self):
        self.bot_service.send_message(self.chat_id, "🔑 please provide your password:")
        
    def ask_for_username(self):
        self.bot_service.send_message(self.chat_id, "👤 Please provide your username:")

    def ask_for_phone_number(self):
        self.bot_service.send_message(self.chat_id, "📱 Please provide your phone number:")

    def ask_for_user_type(self):
        self.bot_service.send_message(
            self.chat_id,
            "🧑‍💼 Choose user type:",
            reply_markup=generate_keyboard([["Customer", "Professional"]])
        )

    def ask_for_entity_type(self):
        self.bot_service.send_message(
            self.chat_id,
            "🏢 Choose entity type:",
            reply_markup=generate_keyboard([["Individual", "Oganization"]])
        )

    def send_registration_success(self):
        self.bot_service.send_message(self.chat_id, "✅ Registration successful! Please verify your email.")

    def send_registration_failure(self):
        self.bot_service.send_message(self.chat_id, "❌ Registration failed. Please try again.")

    def send_login_success(self):
        self.bot_service.send_message(self.chat_id, "🎉 Login successful!")

    def send_login_failure(self,error=None):
        self.bot_service.send_message(self.chat_id, "❌ Login failed. Check your credentials.",error)

    def send_help_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "ℹ️ You can use the following options:\n"
            "- 📝 Register: Create a new account\n"
            "- 🔐 Login: Access your existing account\n"
            "- ❌ Cancel: Cancel the current operation"
        )
