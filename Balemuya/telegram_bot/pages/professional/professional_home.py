import requests
import re
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import pytz
class ProfessionalMenu:
    def __init__(self, bot_service,auth_service, chat_id):
        self.bot_service = bot_service
        self.auth_service=auth_service
        self.chat_id = chat_id

    def display_menu(self):
        self.auth_service.set_user_state("professional_menu")
        print('user state is', self.auth_service.get_user_state())
        if not self.auth_service:
            self.auth_service.get_logged_in_user()
        menu_text = f"Welcome {self.auth_service.user_instance['user']['full_name']} to Balemuya Professional Menu!"
        keyboard = {
            "keyboard": [
                ["Manage Requests", "Manage Services"],
                ["Payment History", "View Subscription"],
                ["Profile", "Help"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_Requests_menu(self):
        menu_text = "Manage Service Requests:"
        keyboard = {
            "keyboard": [
                ["Pending Requests", "Accepted Requests"],
                ["Rejected Requests", "Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_service_menu(self):
        menu_text = "Manage Your Services as a Professional:"
        keyboard = {
            "keyboard": [
                ["New Jobs", "Completed Job Bookings"],
                ["Rejected Job Applications","Canceled Job Applications","Pending Job Applications"],
                [ "Back to Main Menu"]
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
        
    def fetch_subscription_plan(self):
        pass
    
    def fetch_payment_history(self):
        pass
    
  

    def fetch_service_posts(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            print('access token',access_token)
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}services/service-posts/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            params = {}
            if status:
                params['status'] = status

            response = requests.get(url, headers=headers, params=params)
            print('response is',response.json())
            print('response status code',response.status_code)
            if response.status_code == 200:
                service_posts = response.json()
                print('Fetched service posts:', service_posts)  # Debugging line
                
                # Construct the message with enhanced formatting
                if service_posts:
                    message = "📋 *Service Posts*\n\n"
                    for post in service_posts:  # Assuming response is a list of posts
                        message += (
                            f"📝 *Title*: {post['title']}\n"
                            f"📅 *date*: {post['work_due_date']}\n"
                            f"🔍 *Status*: {post['status']}\n"
                            f"📌 *Details*: {post.get('description', 'No details provided')}\n\n"
                        )
                    self.bot_service.send_message(self.chat_id, message)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No service posts available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service posts.")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service posts: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service posts.")
  

    def fetch_service_applications(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            print('Access token:', access_token)
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/professional/services/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            params = {}
            if status:
                params['status'] = status

            response = requests.get(url, headers=headers, params=params)
            print('Response Status Code:', response.status_code)
            print('Response Content:', response.json())

            if response.status_code == 200:
                service_posts = response.json().get('data', [])
                print('Fetched service posts:', service_posts)  # Debugging line
                
                if service_posts:
                    message = "📋 Service Posts Applications\n\n"

                    for post in service_posts:
                        service = post['service']
                        customer = post['customer']

                        # Format the work due date
                        work_due_date = datetime.strptime(service['work_due_date'], "%Y-%m-%dT%H:%M:%S.%fZ")  # Parse the date
                        local_due_date = work_due_date.astimezone(pytz.timezone('Africa/Addis_Ababa')).strftime("%d %B %Y")  # Set to Ethiopia timezone

                        message += (
                            f"📝 Title: {service['title']}\n"
                            f"📂 Category: {service['category']}\n"
                            f"⚡ Urgency: {service['urgency']}\n"
                            f"📅 Due Date: {local_due_date}\n"
                            f"🔍 Status: {post['status']}\n"
                            f"📜 Description: {service['description']}\n"
                            f"📍 Location: {service['location']['city'] or 'N/A'}, {service['location']['country']}\n"
                            f"👤 Customer: {customer['customer_name']}\n"
                            f"📷 Customer Image: {customer['customer_profile_image'] or 'No image provided'}\n"
                            f"💬 Message: {post.get('message', 'No message provided')}\n\n"
                        )
                    
                    self.bot_service.send_message(self.chat_id, message)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No service applications available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service applications.")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service applications: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service applications.")

            
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
    
   