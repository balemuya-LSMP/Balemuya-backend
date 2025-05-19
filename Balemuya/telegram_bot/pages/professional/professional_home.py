import requests
import re
from django.core.cache import cache
from django.conf import settings
class ProfessionalMenu:
    def __init__(self, bot_service,auth_service, chat_id):
        self.bot_service = bot_service
        self.auth_service=auth_service
        self.chat_id = chat_id

    def display_menu(self):
        # self.auth_service.get_logged_in_user()
        self.auth_service.set_user_state("professional_menu")
        print('user state is', self.auth_service.get_user_state())
        if not self.auth_service:
            self.auth_service.get_logged_in_user()
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
    
    def fetch_professional_profile(self):
        profile = self.auth_service.user_instance
        print('User instance is:', profile)  # Debugging line

        if 'user' in profile:
            user_info = profile['user']  # Directly access user since profile['user'] is the relevant object
            
            # Construct the message with enhanced formatting
            message = (
                f"✨ *Profile of {user_info['full_name']}* ✨\n\n"
                f"📷 *Profile Image*: (Image sent above)\n"
                f"📧 *Email*: {user_info['email']}\n"
                f"👤 *Username*: @{user_info['username']}\n"
                f"📞 *Phone Number*: {user_info['phone_number']}\n"
                f"🏢 *Organization*: {user_info['org_name']}\n"
                f"📝 *Bio*: {user_info.get('bio', 'No bio provided')}\n"
                f"📍 *Address*: {user_info['address']['city']}, {user_info['address']['region']}, {user_info['address']['country']}\n"
                f"🌟 *Rating*: {profile['rating']}\n"
                f"🛠️ *Years of Experience*: {profile['years_of_experience']}\n"
                f"💰 *Balance*: ${profile['balance']}\n"
                f"✅ *Available*: {'Yes' if profile['is_available'] else 'No'}\n"
                f"🔒 *Verified*: {'Yes' if profile['is_verified'] else 'No'}\n"
            )

            self.bot_service.send_photo(self.chat_id, user_info['profile_image_url'])

            self.bot_service.send_message(self.chat_id, message)
            self.auth_service.set_user_state('professional_menu')
        else:
            self.bot_service.send_message(self.chat_id, "⚠️ Profile information is not available.")
            self.auth_service.set_user_state('professional_menu')
    
   