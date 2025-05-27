from users.models import User,Customer,Professional
from common.serializers import UserSerializer
from users.serializers import CustomerSerializer,ProfessionalSerializer


import requests
import re
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import pytz
from PIL import Image, ImageDraw
from io import BytesIO
from  ...utils.common import create_circular_image,format_date
from ...handlers.job_handler import JobHandler
from .callbacks import CustomerCallbackHandler
class CustomerMenu:
    def __init__(self, bot_service,auth_service, chat_id):
        self.bot_service = bot_service
        self.auth_service=auth_service
        self.chat_id = chat_id
        self.job_handler = JobHandler(self)
        self.customer_callback_handler=CustomerCallbackHandler(bot_service,auth_service)

    def display_menu(self):
        print('user state is', self.auth_service.get_user_state())
        if not self.auth_service:
            self.auth_service.get_logged_in_user()
        text='Choose options Below'
        keyboard = {
            "keyboard": [
                ["📅 Manage Requests","🛠️ Manage Services"],
                ["👥 View Professionals", "⭐ View Favorites"],
                ["👤 View Profile","🔙 Back to Main Menu", "🔓 Logout"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id,text,reply_markup=keyboard)

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
        menu_text = "Manage Your Services:"
        keyboard = {
            "keyboard": [
                ["🆕 Post New Job","View Posts" ], 
                ["✅ Completed Bookings","🔄 Active Bookings", "❌ Canceled Bookings"],
                ["🔙 Back to Main Menu"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        self.bot_service.send_message(self.chat_id, menu_text, reply_markup=keyboard)
    def post_new_job(self):
        self.auth_service.set_user_state("waiting_for_job_title")
        self.bot_service.send_message(self.chat_id, "🏗️ Please enter the job title:")
    
    def handle_user_response(self, text):
        user_state = self.auth_service.get_user_state()
        print('user state is', user_state)
        
        if user_state == "waiting_for_booking_report_reason":
            booking_id = self.customer_callback_handler.pending_booking_reports.pop(self.chat_id, None)
            if booking_id:
                # Call the method that processes the booking report
                self.customer_callback_handler.report_booking(self.chat_id, booking_id, text)
                self.auth_service.set_user_state(None)  # Reset the state
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ No booking to report found.")
                self.display_service_menu()

        if user_state == "waiting_for_job_title":
            self.job_handler.handle(text, user_state)
        elif user_state == "waiting_for_job_description":
            self.job_handler.handle(text, user_state) 
        elif user_state == "waiting_for_job_category":
            self.job_handler.handle(text, user_state) 
        elif user_state == "waiting_for_job_urgency":
            self.job_handler.handle(text, user_state) 
        elif user_state == "waiting_for_work_due_date":
            self.job_handler.handle(text, user_state)
        elif user_state == "waiting_for_location":
            print('text is at location',text)
            # Added condition for location
            self.job_handler.handle(text, user_state)
        elif text == "🆕 Post New Job":
            self.post_new_job()  # Start the job posting process
        else:
            print('user_state is', user_state)
            print('text is', text)
            self.bot_service.send_message(self.chat_id, "⚠️ Please select a valid option.")
            
    def fetch_nearby_professionals(self):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(self.chat_id, "⚠️ Unable to fetch nearby professionals. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/customer/nearby-professionals/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            print('Response Status Code:', response.status_code)  # Debugging line
            
            if response.status_code == 200:
                data = response.json()
                if data['message'] == "success" and data['nearby_professionals']:
                    professionals = data['nearby_professionals']
                    message = "👥 *Nearby Professionals*\n\n"
                    
                    for pro in professionals:
                        profile_image = pro.get('profile_image', '')
                        name = pro.get('name', 'Unknown')
                        bio = pro.get('bio', 'No bio available')
                        address = pro.get('address', {})
                        rating = pro.get('rating','0')
                        location = f"{address.get('city', 'Unknown')}, {address.get('region', 'Unknown')}, {address.get('country', 'Unknown')}"
                        distance = pro.get('distance', 0.0)

                        message += (
                            f"----------------------------------------------\n"
                            f"👤 Name: {name}\n"
                            f"📍 Location: {location}\n"
                            f"🌟 Bio: {bio}\n"
                            f"📏 Distance: {distance} km away \n"
                            f"⭐ rating: {rating}\n"
                            f"----------------------------------------------\n\n"
                        )
                        
                        # Inline keyboard for actions
                        inline_keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "🛠️ Request Service", "callback_data": f"request_service_{pro['id']}"},
                                    {"text": "⭐ Add to Favorites", "callback_data": f"add_to_favorites_{pro['id']}"},
                                    {"text": "🔍 View Details", "callback_data": f"view_prof_details_{pro['id']}"}
                                ]
                            ]
                        }

                        self.bot_service.send_message(self.chat_id, message, reply_markup=inline_keyboard)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ No nearby professionals found.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch nearby professionals. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching nearby professionals: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching nearby professionals.")
            
            
    
    #fetch favorite
    def fetch_favorites(self):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(self.chat_id, "⚠️ Unable to fetch favorites. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/favorites/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            print('Response Status Code:', response.status_code)  # Debugging line
            
            if response.status_code == 200:
                favorites = response.json()
                if favorites:
                    message = "⭐ *Your Favorited Professionals*\n\n"
                    
                    for item in favorites:
                        pro = item.get('professional', {})
                        profile_image = pro.get('profile_image_url', '')
                        full_name = pro.get('full_name', 'Unknown')
                        bio = pro.get('bio', 'No bio available')
                        address = pro.get('address', {})
                        location = f"{address.get('city', 'Unknown')}, {address.get('region', 'Unknown')}, {address.get('country', 'Unknown')}"
                        phone_number = pro.get('phone_number', 'Not provided')

                        message += (
                            f"----------------------------------------------\n"
                            f"👤 Name: {full_name}\n"
                            f"📍 Location: {location}\n"
                            f"📞 Phone: {phone_number}\n"
                            f"🌟 Bio: {bio}\n"
                            f"----------------------------------------------\n\n"
                        )
                        
                        # Inline keyboard for actions
                        inline_keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "🛠️ Request Service", "callback_data": f"request_service_{pro['id']}"},
                                    {"text": "⭐ Remove from Favorites", "callback_data": f"remove_from_favorites_{pro['id']}"},
                                    {"text": "🔍 View Details", "callback_data": f"view_details_{pro['id']}"}
                                ]
                            ]
                        }

                        self.bot_service.send_message(self.chat_id, message, reply_markup=inline_keyboard)
                else:
                    self.bot_service.send_message(self.chat_id, "⚠️ You have no favorited professionals.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch favorites. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching favorites: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching your favorites.")
    
    
    
  
    def fetch_service_posts(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            print('Access token:', access_token)
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/customer/services/"
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
                service_posts = response.json().get("data", [])
                print('Fetched service posts:', service_posts)

                if service_posts:
                    message = "✨ *Service Posts*\n\n"
                    for post in service_posts:
                        created_at = post.get('created_at')
                        work_due_date = post.get('work_due_date')
                        print('------------work due date is', work_due_date)
                        if created_at:
                            created_at = format_date(created_at)
                        if work_due_date:
                            work_due_date = format_date(work_due_date)

                        customer = post['customer']['user']
                        message += (
                            f"📝 Title: {post['title']}\n"
                            f"📂 Category: {post['category']}\n"
                            f"📅 Due Date: {work_due_date}\n"
                            f"✅ Status: {post['status']}\n"
                            f"👤 Customer Name: {customer['full_name']} (Type: {customer['entity_type']})\n"
                            f"⭐ Previous Rating: {post['customer']['rating'] or 'No rating'}\n"
                            f"📌 Details: {post.get('description', 'No details provided')}\n\n"
                            f"📍 Location: {post['location'].get('city', 'Unknown')}, "
                            f"{post['location'].get('region', 'Unknown')}\n"
                            f"⏰ Posted At: {created_at}\n"
                            f"-----------------------------------------------------------------------------\n\n"
                        )

                        # Adding the service post ID to the callback data for Edit and Delete
                        reply_markup = {
                            "inline_keyboard": [
                                [
                                    {"text": "✏️ Edit", "callback_data": f"edit_service_{post['id']}"},
                                    {"text": "🗑️ Delete", "callback_data": f"delete_service_{post['id']}"}
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

            url = f"{settings.BACKEND_URL}users/customer/services/"
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
                        service = post.get('service', {})
                        professional = post.get('professional', {})
                        customer = post.get('customer', {})

                        # Format the scheduled date
                        scheduled_date = post.get('scheduled_date')
                        if scheduled_date:
                            scheduled_date = format_date(scheduled_date)

                        message = ""
                        
                        if status in ['booked', 'completed']:
                            message = (
                                f"📝 Service Title: {service.get('title', 'N/A')}\n"
                                f"📂 Category: {service.get('category', 'N/A')}\n"
                                f"⚡ Urgency: {service.get('urgency', 'N/A')}\n"
                                f"📅 Scheduled Date: {scheduled_date or 'N/A'}\n"
                                f"🔍 Status: {post.get('status', 'N/A')}\n"
                                f"📜 Description: {service.get('description', 'N/A')}\n"
                                f"👤 Professional: {professional.get('professional_name', 'N/A')}\n"
                                f"📞 Phone: {professional.get('phone_number', 'N/A')}\n"
                                f"⭐ Rating: {professional.get('rating', 'No rating')}\n"
                                f"👤 Customer: {customer.get('customer_name', 'N/A')}\n"
                                f"📍 Location: {service.get('location', {}).get('city', 'N/A')}, {service.get('location', {}).get('country', 'N/A')}\n"
                                "-------------------------------------------------------\n"
                            )
                        elif status is None or status == 'pending':
                            work_due_date = post.get('work_due_date')
                            if work_due_date:
                                work_due_date = format_date(work_due_date)

                            message = (
                                f"📝 Service Title: {service.get('title', 'N/A')}\n"
                                f"📂 Category: {post.get('category', 'N/A')}\n"
                                f"⚡ Urgency: {post.get('urgency', 'N/A')}\n"
                                f"📅 Work Due Date: {work_due_date or 'N/A'}\n"
                                f"🔍 Status: {post.get('status', 'N/A')}\n"
                                f"📜 Description: {post.get('description', 'N/A')}\n"
                                f"📍 Location: {post.get('location', {}).get('city', 'N/A')}, {service.get('location', {}).get('country', 'N/A')}\n"
                                "-------------------------------------------------------\n"
                            )

                        # Create the inline keyboard based on status
                        if status in ['booked']:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "❌ Cancel", "callback_data": f"cancel_booking_{post['id']}"},
                                        {"text": "✅ Mark as Completed", "callback_data": f"complete_booking_{post['id']}"}
                                    ]
                                ]
                            }
                        elif status in ['completed']:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "💳 Pay Now", "callback_data": f"pay_for_booking_{post['id']}"},
                                    ],
                                    [
                                        {"text": "🚨 Report", "callback_data": f"report_booking_{post['id']}"},
                                        {"text": "📝 Review", "callback_data": f"review_booking_{post['id']}"}
                                    ],
                                ]
                            }
                        elif status is None or status == 'pending':
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "✏️ Edit Post", "callback_data": f"edit_post_{post['id']}"},
                                        {"text": "🗑️ Delete Post", "callback_data": f"delete_post_{post['id']}"},
                                    ],
                                    [
                                        {"text": "View Applications", "callback_data": f"view_post_apps{post['id']}"},
                                    ]
                                ]
                            }
                        else:
                            reply_markup = None

                        self.bot_service.send_message(self.chat_id, message, reply_markup=reply_markup)

                else:
                    self.bot_service.send_message(self.chat_id, f"⚠️ No {status} service bookings available.")
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Failed to fetch service bookings.")
                    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching service bookings: {e}")  # Debugging line
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching service bookings.")
            
   
    def fetch_customer_profile(self):
        try:
            profile = self.auth_service.user_instance
            print('User instance is:', profile) 

            if 'user' in profile:
                user_info = profile['user']
                
                message = (
                    f"✨ Profile of {user_info['full_name']} ✨\n\n"
                    f"🏢 Name : {user_info['full_name']}\n\n"
                    f"📷 Profile Image:  (Image sent above)\n\n"
                    f"📧 Email : {user_info['email']}\n\n"
                    f"👤 Username:  @{user_info['username']}\n\n"
                    f"📞 Phone Number:  {user_info['phone_number']}\n\n"
                    f"🏢 Entity Type:  {user_info['entity_type']}\n\n"
                    f"📝 Bio : {user_info.get('bio', 'No bio provided')}\n\n"
                    f"📍 Address : {user_info['address']['city']}, "
                    f"{user_info['address']['region']}, {user_info['address']['country']}\n\n"
                    f"🌟 Rating : {profile.get('rating', '0')}\n\n"
                    f"📅 Number of Services Booked : {profile.get('number_of_services_booked', '0')}\n\n"
                    f"🚨 Number of Reports : {profile.get('report_count', '0')}\n\n"
                    f"----------------------------------------------\n\n"
                )

                self.bot_service.send_photo(self.chat_id, user_info['profile_image_url'])
                self.bot_service.send_message(self.chat_id, message)
                # self.auth_service.set_user_state('customer_menu')
            else:
                self.bot_service.send_message(self.chat_id, "⚠️ Profile information is not available.")
                # self.auth_service.set_user_state('customer_menu')
        except requests.exceptions.RequestException as e:
            print(f"Error at fetching profile: {e}")
            self.bot_service.send_message(self.chat_id, "⚠️ An error occurred while fetching the profile.")
    
    
    def fetch_service_requests(self, status=None):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/customer/service-requests/"
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
                        customer_address = customer.get('address', None)

                        if customer_address:
                            customer_city = customer_address.get('city', 'Unknown City')
                        else:
                            customer_city = 'Unknown City'

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

                        if request['status'] in ["accepted"]:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "❌ Cancel Request", "callback_data": f"reject_request_{request['id']}"}
                                    ],
                                ]
                            }
                        elif request['status'] in ["completed"]:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "💳 Pay Now", "callback_data": f"pay_completed_request_{request['id']}"},
                                    ],
                                    [
                                        {"text": "📝 Review", "callback_data": f"review_completed_request_{request['id']}"},
                                        {"text": "🚨 Report", "callback_data": f"report_completed_request_{request['id']}"}
                                    ],
                                ]
                            }
                        elif request['status'] in ["canceled"]:
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "📝 Review", "callback_data": f"review_canceled_request_{request['id']}"},
                                        {"text": "🚨 Report", "callback_data": f"report_canceled_request_{request['id']}"}
                                    ],
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