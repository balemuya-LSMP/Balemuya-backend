import requests
import re
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import pytz
from PIL import Image, ImageDraw
from io import BytesIO
from  ...utils.common import create_circular_image
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
                ["Profile", "Help","🔐 Logout"]
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
                ["New Jobs", "Completed Job Bookings","Canceled Job Bookings"],
                ["Rejected Job Applications","Accepted Job Applications","Pending Job Applications"],
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
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(self.chat_id, "⚠️ Unable to fetch subscription plans. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/professional/subscription/history/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            print('response text is',response)
            print('Response Status Code:', response.status_code)  # Debugging line
            
            if response.status_code == 200:
                subscription_plans = response.json()
                print('subscription plans ',subscription_plans)
                if subscription_plans:
                    message = "📋 *Subscription Plans*\n\n"
                    for plan in subscription_plans:
                        message += (
                            f"🌟 *Plan Type*: {plan['plan_type']}\n"
                            f"💰 *Price*: {plan['cost']} Birr\n"
                            f"🗓️ *Duration*: {plan['duration']} days\n"
                            f"🗓️ *Start Date*: {plan['start_date']} days\n"
                            f"🗓️ *End Date*: {plan['end_date']} days\n"
                            f"---------------\n"
                        )
                    self.bot_service.send_message(self.chat_id, message)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No subscription plans available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch subscription plans. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching subscription plans: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching subscription plans.")
            
    def fetch_payment_history(self):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(self.chat_id, "⚠️ Unable to fetch subscription plans. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/professional/subscription/history/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            print('response text is',response)
            print('Response Status Code:', response.status_code)  # Debugging line
            
            if response.status_code == 200:
                subscription_plans = response.json()
                print('subscription plans ',subscription_plans)
                if subscription_plans:
                    message = "📋 *Subscription Plans*\n\n"
                    for plan in subscription_plans:
                        message += (
                            f"🌟 *Plan Type*: {plan['plan_type']}\n"
                            f"💰 *Price*: {plan['cost']} Birr\n"
                            f"🗓️ *Duration*: {plan['duration']} days\n"
                            f"🗓️ *Start Date*: {plan['start_date']} days\n"
                            f"🗓️ *End Date*: {plan['end_date']} days\n"
                            f"---------------\n"
                        )
                    self.bot_service.send_message(self.chat_id, message)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No subscription plans available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch subscription plans. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching subscription plans: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching subscription plans.")
    
    
    
  
    def fetch_service_posts(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            print('Access token:', access_token)
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
            print('Response:', response.json())
            print('Response status code:', response.status_code)

            if response.status_code == 200:
                service_posts = response.json()
                print('Fetched service posts:', service_posts)

                if service_posts:
                    message = "✨ *Service Posts*\n\n"
                    for post in service_posts:
                        message += (
                            f"📝 *Title*: {post['title']}\n"
                            f"📂 *Category*: {post['category']}\n"
                            f"📅 *Due Date*: {post['work_due_date']}\n"
                            f"✅ *Status*: {post['status']}\n"
                            f"👤 *Customer Name*: {post['customer']['user']['full_name']} (Type: {post['customer']['user']['entity_type']})\n"
                            f"⭐ *Previous Rating*: {post['customer']['rating']}\n"
                            f"📌 *Details*: {post.get('description', 'No details provided')}\n\n"
                            f"📍 *Location*: {post['location']['city']}, {post['location']['region']}\n"
                            f"⏰ *Posted At*: {post['created_at']}\n"
                            f"---\n"
                        )

                        # Adding the service post ID to the callback data
                        reply_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "✉️ Apply", "callback_data": f"apply_service_{post['id']}"}
                                ]
                            ]
                        }

                    self.bot_service.send_message(self.chat_id, message, reply_markup=reply_markup)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No service posts available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service posts.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching service posts: {e}")
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

                        # Check if work_due_date is not None
                        work_due_date_str = service.get('work_due_date')
                        if work_due_date_str:
                            work_due_date = datetime.strptime(work_due_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")  # Parse the date
                            local_due_date = work_due_date.astimezone(pytz.timezone('Africa/Addis_Ababa')).strftime("%d %B %Y")  # Set to Ethiopia timezone
                        else:
                            local_due_date = 'N/A'  # Default value if date is not available

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
                    self.bot_service.send_message(self.chat_id,f"⚠️ No {status} service applications available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service applications.")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service applications: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service applications.")
    
    
    def fetch_service_booking(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            print('Access token:', access_token)
            
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/professional/services/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            # Set up parameters for the request
            params = {}
            if status:
                params['status'] = status

            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            print('Response Status Code:', response.status_code)

            # Check the response status
            if response.status_code == 200:
                service_posts = response.json().get('data', [])
                print('Fetched service posts:', service_posts)  # Debugging line
                
                if service_posts:
                    for post in service_posts:
                        service = post['service']
                        professional = post['professional']
                        customer = post['customer']
                        # Format the scheduled date
                        scheduled_date_str = post.get('scheduled_date')
                        if scheduled_date_str:
                            scheduled_date = datetime.strptime(scheduled_date_str, "%Y-%m-%dT%H:%M:%SZ")
                            local_scheduled_date = scheduled_date.astimezone(pytz.timezone('Africa/Addis_Ababa')).strftime("%d %B %Y")
                        else:
                            local_scheduled_date = 'N/A'

                        # Format the message for the user
                        message = (
                            f"*📝 Service Title:* {service['title']}\n"
                            f"*📂 Category:* {service['category']}\n"
                            f"*⚡ Urgency:* {service['urgency']}\n"
                            f"*📅 Scheduled Date:* {local_scheduled_date}\n"
                            f"*🔍 Status:* {post['status']}\n"
                            f"*📜 Description:* {service['description']}\n"
                            f"*👤 Customer:* {customer['customer_name']}\n"
                            f"*📍 Location:* {service['location']['city'] or 'N/A'}, {service['location']['country']}\n"
                            f"---\n"
                        )

                        # Create the inline keyboard
                        reply_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "Apply", "callback_data": "apply_service"}
                                ]
                            ]
                        }

                        # Send the message with the inline keyboard
                        self.bot_service.send_message(self.chat_id, message, reply_markup=reply_markup)
                else:
                    self.bot_service.send_message(self.chat_id, f"⚠️ No {status} service bookings available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service bookings.")
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service bookings: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service bookings.")
   
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
    
   