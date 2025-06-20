from .telegram_bot_services import TelegramBotService
from .telegram_auth_services import TelegramAuthService
from ..utils.keyboard import generate_keyboard
from ..handlers.registration_handler import RegistrationHandler
from ..handlers.login_handler import LoginHandler
from ..pages.customer.customer_home import CustomerMenu
from ..pages.professional.professional_home import ProfessionalMenu
from ..pages.professional.callbacks import ProfessionalCallbackHandler
from ..pages.customer.callbacks import CustomerCallbackHandler
from django.conf import settings

class TelegramFacade:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.bot_service = TelegramBotService(settings.TELEGRAM_BOT_TOKEN)
        self.auth_service = TelegramAuthService(chat_id)

        self.registration_handler = RegistrationHandler(self)
        self.login_handler = LoginHandler(self)
        self.customer_menu = None
        self.professional_menu = None 
        self.professional_callback_handler = ProfessionalCallbackHandler(self.bot_service, self.auth_service)
        self.customer_callback_handler = CustomerCallbackHandler(self.bot_service, self.auth_service)
    
    def send_main_menu(self, message="Please choose an option:"):
        try:
            is_logged_in = self.auth_service.get_session_data("is_logged_in")
            user_state = self.auth_service.get_user_state()

            if is_logged_in and user_state == 'professional_menu': 
                self.send_professional_menu()
            elif is_logged_in and user_state == 'customer_menu': 
                self.send_customer_menu()
            else:
                keyboard = [
                    ["📝 Register", "🔐 Login"],
                    ["ℹ️ Help", "❌ Cancel"]
                ]
                self.bot_service.send_message(
                    self.chat_id,
                    message,
                    reply_markup=generate_keyboard(keyboard)
                )
        except Exception as e:
            print(f"Error in send_main_menu: {e}")
            self.bot_service.send_message(
                self.chat_id,
                "An error occurred. Please try again later."
            )

    def handle_update(self, update):
        if update.get("callback_query"):
            self.handle_callback_query(update["callback_query"])
        else:
            message = update.get("message", {})
            text = message.get("text", "")
            user_state = self.auth_service.get_user_state()
            user_type = self.auth_service.get_user_type()
            self.dispatch(text, user_state, user_type)

    def handle_callback_query(self, callback_query):
        user_type = self.auth_service.get_user_type()
        if user_type == 'professional':
            self.professional_callback_handler.handle_callback_query(callback_query)
        elif user_type == 'customer':
            self.customer_callback_handler.handle_callback_query(callback_query)
    def dispatch(self, text, user_state, user_type=None):
        is_logged_in = self.auth_service.get_session_data("is_logged_in")

        if text == "/start" and user_type is None:
            self.send_welcome_message()
        elif text in ["/cancel", "❌ Cancel"]:
            self.auth_service.clear_session()
            self.send_cancel_message()
        elif text in ["🔓 Logout"]:
            self.auth_service.logout_user()
            self.auth_service.clear_session()
            self.send_logout_message()
        elif text == "ℹ️ Help":
            self.send_help_message()
        elif text == "📝 Register" or (user_state and user_state.startswith("waiting_for_") and "register" in user_state):
            self.registration_handler.handle(text, user_state)
        elif text == "🔐 Login" or (user_state and user_state.startswith("waiting_for_") and "login" in user_state):
            self.login_handler.handle(text, user_state)
        elif is_logged_in or self.auth_service.user_instance:
            menu_state = self.auth_service.get_menu_state()
            if menu_state == "customer_menu" and user_type== 'customer':
                if not self.customer_menu:
                    self.send_customer_menu()
                self.handle_customer_commands(text)
            elif menu_state == "professional_menu" or user_type== 'professional':
                if not self.professional_menu:
                    self.send_professional_menu()
                self.handle_professional_commands(text)
        else:
            self.send_main_menu("⚠️ Unknown command. Please select an option.")
    def handle_customer_commands(self, text):

        if text == "🛠️ Manage Services":
            self.customer_menu.display_service_menu()
        elif text == "🆕 Post New Job":
            self.customer_menu.post_new_job()
        elif text == "View Posts":
            self.customer_menu.fetch_service_booking()
        elif text == "🔄 Active Bookings":
            self.customer_menu.fetch_service_booking(status='booked')
        elif text == "✅ Completed Bookings":
            self.customer_menu.fetch_service_booking(status='completed')
        elif text == "❌ Canceled Bookings":
            self.customer_menu.fetch_service_booking(status='canceled')
        elif text == "Service Applications":
            self.customer_menu.display_service_applications_menu()
        elif text == "Bookings":
            self.customer_menu.display_bookings_menu()
        elif text == "📅 Manage Requests":
            self.customer_menu.display_requests_menu()
        elif text == "⌛ Pending Requests":
            self.customer_menu.fetch_service_requests(status='pending')
        elif text == "✅ Accepted Requests":
            self.customer_menu.fetch_service_requests(status='accepted')
        elif text == "❌ Rejected Requests":
            self.customer_menu.fetch_service_requests(status='rejected')
        elif text == "✅ Completed Requests":
            self.customer_menu.fetch_service_requests(status='completed')
        elif text == "👤 View Profile":
            self.customer_menu.fetch_customer_profile()
        elif text == "⭐ View Favorites":
            self.customer_menu.fetch_favorites()
        elif text == "👥 View Professionals":
            self.customer_menu.fetch_nearby_professionals()
        elif text == "🔙 Back to Main Menu":
            self.send_customer_menu()
        else:
            self.customer_menu.handle_user_response(text)


    def handle_professional_commands(self, text):
        if text == "💳 Payment History":
            self.professional_menu.fetch_payment_history()
        elif text == "🛠️ Manage Services":
            self.professional_menu.display_service_menu()
        elif text == "🆕 New Jobs":
            self.professional_menu.fetch_service_posts(status='active')
            
        elif text == "🔄 Active Bookings":
            self.professional_menu.fetch_service_booking(status='booked')
        elif text == "✅ Completed Job Bookings":
            self.professional_menu.fetch_service_booking(status='completed')
        elif text == "❌ Canceled Job Bookings":
            self.professional_menu.fetch_service_booking(status='canceled')    
            
        elif text == "🔄 Pending Job Applications":
            self.professional_menu.fetch_service_applications(status='pending')
        elif text == "📄 Rejected Job Applications":
            self.professional_menu.fetch_service_applications(status='rejected')
        elif text == "✔️ Accepted Job Applications":
            self.professional_menu.fetch_service_applications(status='accepted')
            
        elif text == "📋 Manage Requests":
            self.professional_menu.display_requests_menu()
        elif text == "⌛ Pending Requests":
            self.professional_menu.fetch_service_requests(status='pending')
        elif text == "✅ Accepted Requests":
            self.professional_menu.fetch_service_requests(status='accepted')
        elif text == "❌ Rejected Requests":
            self.professional_menu.fetch_service_requests(status='rejected')
        elif text == "✅ Completed Requests":
            self.professional_menu.fetch_service_requests(status='completed')
            
        elif text == "📄 View Subscription":
            self.professional_menu.fetch_subscription_plan()
        elif text == "👤 View Profile":
            self.professional_menu.fetch_professional_profile()
        elif text == "🔙 Back to Main Menu":
            self.professional_menu.display_menu()
        else:
            self.bot_service.send_message(self.chat_id, "⚠️ Unknown professional command. Please select from options.")

    def send_customer_menu(self):
        self.customer_menu = CustomerMenu(self.bot_service, self.auth_service, self.chat_id)
        self.customer_menu.display_menu()

    def send_professional_menu(self):
        self.professional_menu = ProfessionalMenu(self.bot_service, self.auth_service, self.chat_id)
        self.professional_menu.display_menu()

    def ask_for_email(self):
        self.bot_service.send_message(self.chat_id, "📧 Please provide your email address:")

    def ask_for_password(self):
        self.bot_service.send_message(self.chat_id, "🔑 Please provide your password:")

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
            reply_markup=generate_keyboard([["Individual", "Organization"]])
        )

    def send_registration_success(self):
        self.bot_service.send_message(self.chat_id, "✅ Registration successful! Please verify your email.")

    def send_registration_failure(self):
        self.bot_service.send_message(self.chat_id, "❌ Registration failed. Please try again.")

    def send_login_success(self):
        self.bot_service.send_message(self.chat_id, "🎉 Login successful!")

    def send_login_failure(self, error=None):
        self.bot_service.send_message(self.chat_id, "❌ Login failed. Check your credentials.")

    def send_help_message(self):
        self.bot_service.send_message(
            self.chat_id,
            "ℹ️ You can use the following options:\n"
            "- 📝 Register: Create a new account\n"
            "- 🔐 Login: Access your existing account\n"
            "- ❌ Cancel: Cancel the current operation"
        )
        self.send_main_menu()
    
    
    def send_welcome_message(self):
        self.send_main_menu("👋 Welcome to Balemuya!\nPlease choose an option:")

    def send_cancel_message(self):
        is_logged_in = self.auth_service.get_session_data("is_logged_in")
        if is_logged_in: 
            user_instance = self.auth_service.user_instance
            if user_instance:
                if user_instance['user']['user_type'] == 'customer':
                    self.send_customer_menu()
                elif user_instance['user']['user_type'] == 'professional':
                    self.send_professional_menu()
        else:
            self.bot_service.send_message(
                self.chat_id,
                "🚫 Operation cancelled. You're back to the main menu.",
                reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help"]])
            )
            
    def send_logout_message(self):
        self.auth_service.set_user_state('logout_user')
        self.bot_service.send_message(
            self.chat_id,
            "🚫 User logged out. You're back to the main menu.",
            reply_markup=generate_keyboard([["📝 Register", "🔐 Login"], ["ℹ️ Help"]])
        )
        
        
        
        
    # elif is_logged_in and self.auth_service.user_instance:
    #         if user_type == 'customer':
    #             # menu_state = self.auth_service.get_menu_state()
    #             if menu_state != "customer_menu":
    #                 self.send_customer_menu()  # Show menu
    #                 self.auth_service.set_menu_state("customer_menu")  # Update menu state
    #             else:
    #                 self.handle_customer_commands(text)  # Handle commands in current menu
    #         elif user_type == 'professional':
    #             # menu_state = self.auth_service.get_menu_state()
    #             if menu_state != "professional_menu":
    #                 self.send_professional_menu()  # Show menu
    #                 self.auth_service.set_menu_state("professional_menu")  # Update menu state
    #             else:
    #                 self.handle_professional_commands(text)  # Handle commands in current menu
    #     else:
    #         self.send_main_menu("⚠️ Unknown command. Please select an option.")