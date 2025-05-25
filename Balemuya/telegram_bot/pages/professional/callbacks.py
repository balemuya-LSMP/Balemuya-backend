import requests
from django.conf import settings
from ...utils.common import format_date

class ProfessionalCallbackHandler:
    def __init__(self, bot_service, auth_service):
        self.bot_service = bot_service
        self.auth_service = auth_service

    def handle_callback_query(self, callback_query):
        callback_data = callback_query.get("data")
        chat_id = callback_query.get("from", {}).get("id")

        if callback_data.startswith("apply_service_"):
            service_post_id = self.extract_service_post_id(callback_data)
            if service_post_id:
                self.process_application(chat_id, service_post_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify the service post.")
        
        elif callback_data.startswith("view_customer_detail_"):
            customer_id = self.extract_customer_id(callback_data)
            if customer_id:
                self.see_customer_detail(chat_id, customer_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not find customer detail.")
        elif callback_data.startswith("accept_request_"):
            request_id = self.extract_request_id(callback_data)
            if request_id:
                self.accept_request(chat_id, request_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify the request.")

        elif callback_data.startswith("reject_request_"):
            request_id = self.extract_request_id(callback_data)
            if request_id:
                self.reject_request(chat_id, request_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify the request.")
                
        elif callback_data.startswith("complete_booking_"):
            booking_id = self.extract_complete_booking_id(callback_data)
            if booking_id:
                self.mark_booking_completed(chat_id, booking_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify booking.")
                
        elif callback_data.startswith("cancel_booking_"):
            booking_id = self.extract_cancel_booking_id(callback_data)
            if booking_id:
                self.cancel_booking(chat_id, booking_id)
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify booking.")
        
        else:
            self.bot_service.send_message(chat_id, "⚠️ Unknown action.")

    def extract_cancel_booking_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None
    def extract_complete_booking_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None
    
    def extract_service_post_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None

    def extract_request_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None
    
    def extract_customer_id(self, callback_data):
        return callback_data.split('_')[3] if len(callback_data.split('_')) > 2 else None

    def process_application(self, chat_id, service_post_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to process application. Access token not found.")
            return
        
        url = f"{settings.BACKEND_URL}services/service-posts/applications/create/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "service_id": service_post_id,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print('Application response:', response.json())  # Log response for debugging
            if response.status_code == 201:
                self.bot_service.send_message(chat_id, "✅ Your application has been submitted successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to submit your application. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error processing application: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while processing your application.")

    def accept_request(self, chat_id, request_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to accept request. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/professional/service-requests/{request_id}/accept/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, "✅ Request accepted successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to accept the request. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error accepting request: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while accepting the request.")

    def reject_request(self, chat_id, request_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to reject request. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}users/professional/service-requests/{request_id}/reject/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, "✅ Request rejected successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to reject the request. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error rejecting request: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while rejecting the request.")
            
    def see_customer_detail(self, chat_id, customer_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to find customer detail.")
            return

        url = f"{settings.BACKEND_URL}users/customer/{customer_id}/profile/"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url, headers=headers)
            print('response is',response)
            if response.status_code == 200:
                customer_data = response.json().get('data', {})
                customer = customer_data.get('customer', {}).get('user', {})
                full_name = customer.get('full_name', '')
                phone_number = customer.get('phone_number', 'No phon Number')
                email = customer.get('email', '')
                bio = customer.get('bio', 'No bio provided')
                address = customer.get('address', {})
                address_info = f"City: {address.get('city', 'Unknown')}, Region: {address.get('region', 'Unknown')}, Country: {address.get('country', 'Unknown')}"

                active_posts = customer_data.get('active_service_posts', [])
                active_posts_info = "\n".join(
                    [f"Title: {post['title']}\nDescription: {post['description']}\nUrgency: {post['urgency']}\nStatus: {post['status']}\nWork Due Date: {format_date(post.get('work_due_date') )}\n" for post in active_posts]
                ) if active_posts else "No active service posts."

                booked_posts = customer_data.get('booked_service_posts', [])
                booked_posts_info = "\n".join(
                    [f"Title: {post['title']}\nDescription: {post['description']}\nStatus: {post['status']}\nWork Due Date: {format_date(post.get('work_due_date') )}\n" for post in booked_posts]
                ) if booked_posts else "No booked service posts."

                completed_posts = customer_data.get('completed_service_posts', [])
                completed_posts_info = "\n".join(
                    [f"Title: {post['title']}\nDescription: {post['description']}\nStatus: {post['status']}\nWork Due Date: {format_date(post.get('work_due_date') )}\n" for post in completed_posts]
                ) if completed_posts else "No completed service posts."

                reviews = customer_data.get('reviews', [])
                reviews_info = "\n".join(
                    [f"Rating: {review['rating']}\nComment: {review['comment']} by {review['user']['full_name']}\n" for review in reviews]
                ) if reviews else "No reviews yet."

                message = (
                    f"-------- Customer Details ---\n"
                    f"Name: {full_name}\n"
                    f"Phone: {phone_number}\n"
                    f"Email: {email}\n"
                    f"Bio: {bio}\n"
                    f"Address: {address_info}\n"
                    f"------------------------------\n\n"
                    f"------------- Active Service Posts ---\n{active_posts_info}"
                    f"------------------------\n\n"
                    f"--------------- Booked Service Posts ---\n{booked_posts_info}"
                    f"--------------------------------------\n\n"
                    f"--- Completed Service Posts ---------------\n{completed_posts_info}"
                    f"-------------------------------------\n\n"
                    f"--------------- Reviews ---------------\n{reviews_info}\n"
                )
                self.bot_service.send_message(chat_id, message)
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to retrieve customer details. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching customer details: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while fetching customer details.")
            
            
    
    def mark_booking_completed(self, chat_id, booking_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to mark booking as completed. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}services/service-bookings/{booking_id}/complete/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, "✅ Booking marked as completed successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to mark booking as completed. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error marking booking as completed: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while marking the booking as completed.")
            
    def cancel_booking(self, chat_id, booking_id):
        access_token = self.auth_service.get_access_token()
        if not access_token:
            self.bot_service.send_message(chat_id, "⚠️ Unable to mark booking as completed. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}services/service-bookings/{booking_id}/cancel/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, "✅ Booking canceled  successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to cancel booking. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error canceling booking : {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while canceling booking.")