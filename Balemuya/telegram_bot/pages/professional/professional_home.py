import requests
import re
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import pytz
from PIL import Image, ImageDraw
from io import BytesIO
from  ...utils.common import create_circular_image,format_date
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
        menu_text = f"Choose Options"
        keyboard = {
        "keyboard": [
            ["📋 Manage Requests", "🛠️ Manage Services"],
            ["💳 Payment History", "📄 View Subscription"],
            ["👤 View Profile","🔓 Logout"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_requests_menu(self):
        menu_text = "View Service Requests:"
        keyboard = {
        "keyboard": [
            ["⌛ Pending Requests", "✅ Accepted Requests"],
            ["✅ Completed Requests","❌ Rejected Requests","🔙 Back to Main Menu"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)

    def display_service_menu(self):
        menu_text = "Manage Your Services as a Professional:"
        keyboard = {
            "keyboard": [
                ["🆕 New Jobs", "🔄 Active Bookings", "✅ Completed Job Bookings", "❌ Canceled Job Bookings"],
                ["📄 Rejected Job Applications", "✔️ Accepted Job Applications", "🔄 Pending Job Applications"],
                ["🔙 Back to Main Menu"]
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
                        start_date=plan['start_date']
                        end_date=plan['end_date']
                        if start_date:
                            start_date=format_date(start_date)
                        if end_date:
                            end_date=format_date(end_date)
                        message += (
                            f"----------------------------------------------\n\n"
                            f"🌟 Plan Type: {plan['plan_type']}\n"
                            f"💰 Price: {plan['cost']} Birr\n"
                            f"🗓️ Duration: {plan['duration']} months\n"
                            f"🗓️ Start Date: {start_date} \n"
                            f"🗓️ End Date: {end_date} \n"
                            f"---------------------------------------------\n\n"
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
            self.bot_service.send_message(self.chat_id, "⚠️ Unable to fetch payments. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/professional/payment/history/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        print('payment history fetched')

        try:
            response = requests.get(url, headers=headers)
            print('Response Status Code:', response.status_code)
            print('Response Content:', response.json())  # Log the response for debugging

            if response.status_code == 200:
                payment_data = response.json()
                subscription_payments = payment_data.get('subscription_payments', [])
                transfer_payments = payment_data.get('transfer_payments', [])

                message = "💰 *Payments Overview*\n\n"

                # Format subscription payments
                message += "📜 *Subscription Payments:*\n"
                if subscription_payments:
                    for payment in subscription_payments:
                        payment_date=payment['payment_date']
                        if payment_date:
                            payment_date = format_date(payment_date)
                        message += (
                            f"----------------------------------------------\n"
                            f"🔹 Amount: {payment['amount']} Birr\n"
                            f"🔹 Payment Date: {payment_date}\n"
                            f"🔹 Status: {payment['payment_status']}\n"
                            f"🔹 Transaction ID: {payment['transaction_id']}\n"
                            f"----------------------------------------------\n"
                        )
                else:
                    message += "⚠️ No subscription payments found.\n"

                # Format transfer payments
                message += "📜 *Transfer Payments:*\n"
                if transfer_payments:
                    for payment in transfer_payments:
                        customer_name = payment['customer']['full_name']
                        amount = payment['amount']
                        payment_date = payment['payment_date']
                        if payment_date:
                            payment_date=format_date(payment_date)
                        status = payment['payment_status']
                        message += (
                            f"------------------------------------------\n"
                            f"🔹 Customer: {customer_name}\n"
                            f"🔹 Amount: {amount} Birr\n"
                            f"🔹 Payment Date: {payment_date}\n"
                            f"🔹 Status: {status}\n"
                            f"-----------------------------------------\n\n"
                        )
                else:
                    message += "⚠️ No transfer payments found.\n"

                self.bot_service.send_message(self.chat_id, message)
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch payments. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching payments: {e}")
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching payments.")
    
    
    
  
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
                        created_at =post.get('created_at')
                        work_due_date =post.get('work_due_date')
                        print('------------work due date is',work_due_date)
                        if created_at:
                            created_at = format_date(created_at)
                        if work_due_date:
                            work_due_date = format_date(work_due_date)
                        message += (
                            f"📝 Title: {post['title']}\n"
                            f"📂 Category: {post['category']}\n"
                            f"📅 Due Date: {work_due_date}\n"
                            f"✅ Status: {post['status']}\n"
                            f"👤 Customer Name: {post['customer']['user']['full_name']} (Type: {post['customer']['user']['entity_type']})\n"
                            f"⭐ Previous Rating: {post['customer']['rating']}\n"
                            f"📌 Details: {post.get('description', 'No details provided')}\n\n"
                            f"📍 Location: {post['location']['city']}, {post['location']['region']}\n"
                            f"⏰ Posted At: {created_at}\n"
                            f"-----------------------------------------------------------------------------\n\n"
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
                        work_due_date = service.get('work_due_date')
                        if work_due_date:
                            work_due_date = format_date(work_due_date) 

                        message += (
                            f"📝 Title: {service['title']}\n"
                            f"📂 Category: {service['category']}\n"
                            f"⚡ Urgency: {service['urgency']}\n"
                            f"📅 Due Date: {work_due_date}\n"
                            f"🔍 Status: {post['status']}\n"
                            f"📜 Description: {service['description']}\n"
                            f"📍 Location: {service['location']['city'] or 'N/A'}, {service['location']['country']}\n"
                            f"👤 Customer: {customer['customer_name']}\n"
                            f"💬 Message: {post.get('message', 'No message provided')}\n\n"
                            f"----------------------------------------------------------------------------\n"

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
                        scheduled_date = post.get('scheduled_date')
                        if scheduled_date:
                            scheduled_date = format_date(scheduled_date)

                        message = (
                            f"*📝 Service Title: {service['title']}\n"
                            f"📂 Category: {service['category']}\n"
                            f"⚡ Urgency: {service['urgency']}\n"
                            f"📅 Scheduled Date: {scheduled_date}\n"
                            f"🔍 Status: {post['status']}\n"
                            f"📜 Description: {service['description']}\n"
                            f"👤 Customer: {customer['customer_name']}\n"
                            f"📍 Location: {service['location']['city'] or 'N/A'}, {service['location']['country']}\n"
                            f"-------------------------------------------------------\n\n"
                        )

                        # Create the inline keyboard
                        if status == 'booked':
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "Report", "callback_data": f"report_booking_{post['id']}"},
                                        {"text": "Review", "callback_data": f"review_booking_{post['id']}"}
                                    ],
                                    [
                                        {"text": "Cancel", "callback_data": f"cancel_booking_{post['id']}"},
                                        {"text": "✅ Mark as Completed", "callback_data": f"complete_booking_{post['id']}"}
                                    ]
                                ]
                            }
                        else:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "Report", "callback_data": f"report_booking_{post['id']}"},
                                        {"text": "Review", "callback_data": f"review_booking_{post['id']}"}
                                    ]
                                ]
                            }

                        self.bot_service.send_message(self.chat_id, message,reply_markup=reply_markup)
                       
                            
                else:
                    self.bot_service.send_message(self.chat_id, f"⚠️ No {status} service bookings available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service bookings.")
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service bookings: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service bookings.")
   
   
    def fetch_professional_profile(self):
        profile = self.auth_service.user_instance
        print('User instance is:', profile) 

        if 'user' in profile:
            user_info = profile['user']
            
            message = (
                f"✨ Profile of {user_info['full_name']} ✨\n\n"
                f"📷 Profile Image: (Image sent above)\n"
                f"📧 Email: {user_info['email']}\n"
                f"👤 Username: @{user_info['username']}\n"
                f"📞 Phone Number: {user_info['phone_number']}\n"
                f"🏢 Organization: {user_info['org_name']}\n"
                f"📝 Bio: {user_info.get('bio', 'No bio provided')}\n"
                f"📍 Address: {user_info['address']['city']}, {user_info['address']['region']}, {user_info['address']['country']}\n"
                f"🌟 Rating: {profile['rating']}\n"
                f"🛠️ Years of Experience: {profile['years_of_experience']}\n"
                f"💰 Balance: {profile['balance']}Birr\n"
                f"✅ Available: {'Yes' if profile['is_available'] else 'No'}\n"
                f"🔒 Verified: {'Yes' if profile['is_verified'] else 'No'}\n"
                f"----------------------------------------------\n\n"

            )

            self.bot_service.send_photo(self.chat_id, user_info['profile_image_url'])

            self.bot_service.send_message(self.chat_id, message)
            self.auth_service.set_user_state('professional_menu')
        else:
            self.bot_service.send_message(self.chat_id, "⚠️ Profile information is not available.")
            self.auth_service.set_user_state('professional_menu')
    
    def fetch_service_requests(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/professional/service-requests/"
            headers = {"Authorization": f"Bearer {access_token}"}

            params = {}
            if status:
                params['status'] = status

            response = requests.get(url, headers=headers, params=params)
            print('Response of service requests is', response)

            if response.status_code == 200:
                service_requests = response.json()
                if service_requests:
                    message = "✨ *Customer Service Requests*\n\n"
                    for request in service_requests:
                        created_at = request.get('created_at')
                        if created_at:
                            created_at = format_date(created_at)

                        customer = request.get('customer', {}).get('user', {})
                        customer_name = customer.get('full_name', 'Unknown Customer')
                        customer_address = customer.get('address', None)  # Address can be None

                        # Check if customer_address is not None before accessing its attributes
                        if customer_address:
                            customer_city = customer_address.get('city', 'Unknown City')
                        else:
                            customer_city = 'Unknown City'  # Default value if address is None

                        customer_phone = customer.get('phone_number', 'No phone number')

                        message += (
                            f"📝 Detail: {request.get('detail', 'No detail provided')}\n"
                            f"🔍 Status: {request.get('status', 'No status provided')}\n"
                            f"👤 Customer: {customer_name}\n"
                            f" Customer Address: {customer_city}\n"
                            f"📞 Phone: {customer_phone}\n"
                            f"⭐ Rating: {request.get('professional', {}).get('rating', 'No rating')}\n"
                            f"📅 Created At: {created_at}\n"
                            f"----------------------------------------------------\n"
                        )

                        if request['status'] in ["", "pending"]:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "✅ Accept", "callback_data": f"accept_request_{request['id']}"},
                                        {"text": "❌ Reject", "callback_data": f"reject_request_{request['id']}"}
                                    ],
                                    [
                                        {"text": "🔍 See Customer Detail", "callback_data": f"view_customer_detail_{customer['id']}"}
                                    ]
                                ]
                            }
                        else:
                            reply_markup = None  # No butt
                        self.bot_service.send_message(self.chat_id, message, reply_markup=reply_markup)

                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No service requests available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service requests.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching service requests: {e}")
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service requests.")