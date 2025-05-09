from users.models import User,Customer,Professional
from common.serializers import UserSerializer
from users.serializers import CustomerSerializer,ProfessionalSerializer


class CustomerMenu:
    def __init__(self, bot_service,auth_service, chat_id):
        self.bot_service = bot_service
        self.auth_service = auth_service
        self.chat_id = chat_id

    def display_menu(self):
        self.auth_service.set_user_state("customer_menu")
        menu_text = f"Welcome {self.auth_service.user_instance['user']['full_name']} to Balemuya Customer Menu!"
        keyboard = {
            "keyboard": [
                ["Service Posts", "Service Applications"],
                ["Bookings", "Profile"],
                ["Help", "Contact Support"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_service_posts_menu(self):
        menu_text = "Manage Your Service Posts:"
        keyboard = {
            "keyboard": [
                ["Active Services", "Pending Services"],
                ["Canceled Services", "Completed Services"],
                ["Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_service_applications_menu(self):
        menu_text = "Manage Your Service Applications:"
        keyboard = {
            "keyboard": [
                ["Pending Applications", "Accepted Applications"],
                ["Rejected Applications", "Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_bookings_menu(self):
        menu_text = "Manage Your Bookings:"
        keyboard = {
            "keyboard": [
                ["Upcoming Bookings", "Completed Bookings"],
                ["Canceled Bookings", "Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_profile_menu(self):
        menu_text = "Manage Your Profile:"
        keyboard = {
            "keyboard": [
                ["View Profile", "Edit Profile"],
                ["Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)