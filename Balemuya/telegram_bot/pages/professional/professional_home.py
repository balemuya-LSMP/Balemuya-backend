class ProfessionalMenu:
    def __init__(self, bot_service,auth_service, chat_id):
        self.bot_service = bot_service
        self.auth_service=auth_service
        self.chat_id = chat_id

    def display_menu(self):
        # self.auth_service.get_logged_in_user()
        self.auth_service.set_user_state("professional_menu")
        print('user state is', self.auth_service.get_user_state())
        menu_text = f"Welcome {self.auth_service.user_instance['user']['full_name']} to Balemuya Professional Menu!"
        keyboard = {
            "keyboard": [
                ["View Applications", "Manage Bookings"],
                ["View Earnings", "Subscription Plans"],
                ["Profile", "Help"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_applications_menu(self):
        menu_text = "Manage Your Applications:"
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
        menu_text = "Manage Your Bookings as a Professional:"
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
        menu_text = "Manage Your Profile as a Professional:"
        keyboard = {
            "keyboard": [
                ["View Profile", "Edit Profile"],
                ["Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)