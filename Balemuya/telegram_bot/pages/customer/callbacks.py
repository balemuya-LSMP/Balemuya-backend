# pages/customer/callback.py
import requests
from django.conf import settings
from ...utils.common import format_date

class CustomerCallbackHandler:
    def __init__(self, bot_service, auth_service):
        self.bot_service = bot_service
        self.auth_service = auth_service
        self.pending_booking_reports = {}
    
    def handle_message(self, update):
        message = update.message
        chat_id = message.chat.id
        text = message.text

        # ✅ Check if user was prompted for a booking report reason
        if chat_id in self.pending_booking_reports:
            booking_id = self.pending_booking_reports.pop(chat_id)
            reason = text
            self.report_booking(chat_id, booking_id, reason)
            return

    def handle_callback_query(self, callback_query):
        callback_data = callback_query.get("data")
        chat_id = callback_query.get("from", {}).get("id")

        if callback_data.startswith("apply_service_"):
            service_post_id = self.extract_id(callback_data, "apply_service_")
            self.process_application(chat_id, service_post_id)

        elif callback_data.startswith("request_service_"):  #done
            prof_id = self.extract_id(callback_data, "request_service_")
            self.send_service_request(chat_id, prof_id)

        elif callback_data.startswith("remove_from_favorites_"):
            prof_id = self.extract_id(callback_data, "remove_from_favorites_")
            self.remove_from_favorites(chat_id, prof_id)

        elif callback_data.startswith("add_to_favorites_"):
            prof_id = self.extract_id(callback_data, "add_to_favorites_")
            self.add_to_favorites(chat_id, prof_id)

        elif callback_data.startswith("view_details_") or callback_data.startswith("view_prof_details_"):
            if callback_data.startswith("view_details_"):
                prof_id = self.extract_id(callback_data, "view_details_")
            else:
                prof_id = self.extract_id(callback_data, "view_prof_details_")
            self.view_profile_of_professional(chat_id, prof_id)

        elif callback_data.startswith("edit_service_"):
            service_post_id = self.extract_id(callback_data, "edit_service_")
            self.edit_service(chat_id, service_post_id)

        elif callback_data.startswith("delete_service_"):
            service_post_id = self.extract_id(callback_data, "delete_service_")
            self.delete_service(chat_id, service_post_id)

        # New handlers from your markup

        elif callback_data.startswith("cancel_booking_"):
            booking_id = self.extract_id(callback_data, "cancel_booking_")
            self.cancel_booking(chat_id, booking_id)

        elif callback_data.startswith("complete_booking_"):
            booking_id = self.extract_id(callback_data, "complete_booking_")
            self.mark_booking_completed(chat_id, booking_id)

        elif callback_data.startswith("pay_for_booking_"):
            booking_id = self.extract_id(callback_data, "pay_for_booking_")
            self.pay_for_booking(chat_id, booking_id)

        elif callback_data.startswith("report_booking_"):
            booking_id = self.extract_id(callback_data, "report_booking_")
            self.pending_booking_reports[chat_id] = booking_id
            
            # Set user state to waiting for booking report reason
            self.auth_service.set_user_state("waiting_for_booking_report_reason")

            self.bot_service.send_message(chat_id, "✍️ Please enter the reason for reporting this booking:")


        elif callback_data.startswith("review_booking_"):
            booking_id = self.extract_id(callback_data, "review_booking_")
            self.review_booking(chat_id, booking_id)

        elif callback_data.startswith("edit_post_"):
            post_id = self.extract_id(callback_data, "edit_post_")
            self.edit_post(chat_id, post_id)

        elif callback_data.startswith("delete_post_"):
            post_id = self.extract_id(callback_data, "delete_post_")
            self.delete_post(chat_id, post_id)

        elif callback_data.startswith("view_post_apps"):
            post_id = self.extract_id(callback_data, "view_post_apps")
            self.view_post_applications(chat_id, post_id)

        elif callback_data.startswith("reject_request_"):
            request_id = self.extract_id(callback_data, "reject_request_")
            self.cancel_request(chat_id, request_id)

        elif callback_data.startswith("pay_completed_request_"):
            request_id = self.extract_id(callback_data, "pay_completed_request_")
            self.pay_for_completed_request(chat_id, request_id)

        elif callback_data.startswith("review_completed_request_"):
            request_id = self.extract_id(callback_data, "review_completed_request_")
            self.review_completed_request(chat_id, request_id)

        elif callback_data.startswith("report_completed_request_"):
            request_id = self.extract_id(callback_data, "report_completed_request_")
            self.report_completed_request(chat_id, request_id)

        elif callback_data.startswith("review_canceled_request_"):
            request_id = self.extract_id(callback_data, "review_canceled_request_")
            self.review_canceled_request(chat_id, request_id)

        elif callback_data.startswith("report_canceled_request_"):
            request_id = self.extract_id(callback_data, "report_canceled_request_")
            self.report_canceled_request(chat_id, request_id)

        else:
            self.bot_service.send_message(chat_id, "⚠️ Unknown action.")

    def extract_id(self, callback_data, prefix):
        return callback_data.replace(prefix, "")

    # Existing method stubs...
    def process_application(self, chat_id, service_post_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to apply for a service.")
                return

            url = f"{settings.BACKEND_URL}services/apply/{service_post_id}/"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, "✅ You have successfully applied for the service!")
            else:
                error_message = response.json().get('detail', 'Failed to apply for the service.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error processing service application: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while applying for the service.")


    def send_service_request(self, chat_id, prof_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to request a service.")
                return

            url = f"{settings.BACKEND_URL}users/customer/service-requests/"
            headers = {"Authorization": f"Bearer {access_token}"}
            data ={
                "professional":prof_id,
                "detail":"I want you your service"
            }
            response = requests.post(url, headers=headers,json=data)
            if response.status_code == 200:
                self.bot_service.send_message(chat_id, f"📨 Your service request has been sent to professional professional.")
            else:
                error_message = response.json().get('detail', 'Failed to send service request.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error sending service request: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while sending the service request.")


    def remove_from_favorites(self, chat_id, prof_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to remove from favorites.")
                return

            url = f"{settings.BACKEND_URL}users/favorites/"
            headers = {"Authorization": f"Bearer {access_token}"}
            data ={
                "professional":prof_id
            }
            response = requests.post(url, headers=headers,json=data)
            
            if response.status_code == 204:
                self.bot_service.send_message(chat_id, f"❌ Professional ID {prof_id} has been removed from your favorites.")
            else:
                error_message = response.json().get('detail', 'Failed to remove from favorites.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error removing from favorites: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while removing from favorites.")

    def add_to_favorites(self, chat_id, prof_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to add to favorites.")
                return

            url = f"{settings.BACKEND_URL}users/favorites/"
            headers = {"Authorization": f"Bearer {access_token}"}
            data ={
                "professional":prof_id
            }
            response = requests.post(url, headers=headers,json=data)
            
            if response.status_code == 201:
                self.bot_service.send_message(chat_id, f"✅ Professional  has been added to your favorites.")
            else:
                error_message = response.json().get('detail', 'Failed to add to favorites.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error adding to favorites: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while adding to favorites.")


    

    def view_profile_of_professional(self, chat_id, prof_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to view profile details.")
                return

            url = f"{settings.BACKEND_URL}users/{prof_id}/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                res_json = response.json()
                data = res_json.get("data", {})
                user = data.get("user", {})
                
                full_name = user.get("full_name", "N/A")
                entity_type = user.get("entity_type", "N/A")
                user_type = user.get("user_type", "N/A")
                email = user.get("email", "N/A")
                phone = user.get("phone_number", "N/A")
                org_name = user.get("org_name", "N/A")
                address = user.get("address", {})
                city = address.get("city", "")
                region = address.get("region", "")
                country = address.get("country", "")
                bio = data.get("description") or user.get("bio") or "No bio available."
                rating = data.get("rating", "N/A")
                years_exp = data.get("years_of_experience", "N/A")
                num_requests = data.get("num_of_request", "N/A")
                is_verified = data.get("is_verified", False)
                is_available = data.get("is_available", False)

                skills = data.get("skills", [])
                skills_list = [skill.get("name") for skill in skills if skill.get("name")]
                skills_str = ", ".join(skills_list) if skills_list else "No skills listed."

                categories = data.get("categories", [])
                categories_list = [cat.get("name") for cat in categories if cat.get("name")]
                categories_str = ", ".join(categories_list) if categories_list else "No categories listed."

                message = (
                    f"👤 Professional Profile:\n"
                    f"Name: {full_name}\n"
                    f"type: {user_type}\n"
                    f"Entity type: {entity_type}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"Location: {city}, {region}, {country}\n"
                    f"Rating: {rating} ⭐\n"
                    f"Years of Experience: {years_exp}\n"
                    f"Verified: {'✅ Yes' if is_verified else '❌ No'}\n"
                    f"Available: {'✅ Yes' if is_available else '❌ No'}\n"
                    f"Skills: {skills_str}\n"
                    f"Categories: {categories_str}\n\n"
                    f"Bio: {bio}"
                )
                self.bot_service.send_message(chat_id, message)

            else:
                error_message = response.json().get('detail', 'Failed to fetch profile details.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching profile details: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while fetching profile details.")

    def edit_service(self, chat_id, service_post_id):
        print(f"Editing service post ID={service_post_id}")
        self.bot_service.send_message(chat_id, f"✏️ Editing service post ID {service_post_id}")

    def delete_service(self, chat_id, service_post_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to delete a service.")
                return

            url = f"{settings.BACKEND_URL}services/service-posts/{service_post_id}/"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                self.bot_service.send_message(chat_id, f"🗑️ Service post has been deleted successfully.")
            else:
                error_message = response.json().get('detail', 'Failed to delete service.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error deleting service post: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while deleting the service post.")


    # New method stubs for added callbacks
    def cancel_booking(self, chat_id, booking_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to cancel a booking.")
                return

            url = f"{settings.BACKEND_URL}services/service-bookings/{booking_id}/cancel/"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(url, headers=headers)  # POST request to cancel booking

            if response.status_code == 200:
                self.bot_service.send_message(chat_id, f"❌ Booking  has been cancelled successfully.")
            else:
                error_message = response.json().get('detail', 'Failed to cancel booking.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error cancelling booking: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while cancelling the booking.")


    def mark_booking_completed(self, chat_id, booking_id):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to mark a booking as completed.")
                return

            url = f"{settings.BACKEND_URL}services/service-bookings/{booking_id}/complete/"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                self.bot_service.send_message(chat_id, f"✅ Booking  marked as completed successfully.")
            else:
                error_message = response.json().get('detail', 'Failed to mark booking as completed.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error marking booking as completed: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while marking the booking as completed.")


    def pay_for_booking(self, chat_id, booking_id):
        print(f"Processing payment for booking ID={booking_id}")
        self.bot_service.send_message(chat_id, f"💳 Payment initiated for booking {booking_id}.")

    def report_booking(self, chat_id, service_post_id, reason):
        try:
            access_token = self.auth_service.get_access_token()
            if not access_token:
                self.bot_service.send_message(chat_id, "⚠️ You must be logged in to report a service post.")
                return

            if not reason:
                self.bot_service.send_message(chat_id, "⚠️ Please provide a reason for reporting the service post.")
                return

            url = f"{settings.BACKEND_URL}services/service-posts/{service_post_id}/report/"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data = {"reason": reason}

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201:
                self.bot_service.send_message(chat_id, f"🚨 Report submitted for service post {service_post_id}.")
            else:
                error_message = response.json().get('detail', 'Failed to submit report.')
                self.bot_service.send_message(chat_id, f"⚠️ {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Error reporting service post: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while submitting the report.")


    def review_booking(self, chat_id, booking_id):
        print(f"Reviewing booking ID={booking_id}")
        self.bot_service.send_message(chat_id, f"📝 Review submitted for booking {booking_id}.")

    def edit_post(self, chat_id, post_id):
        print(f"Editing post ID={post_id}")
        self.bot_service.send_message(chat_id, f"✏️ Editing post ID {post_id}.")

    def delete_post(self, chat_id, post_id):
        print(f"Deleting post ID={post_id}")
        self.bot_service.send_message(chat_id, f"🗑️ Deleted post ID {post_id}.")

    def view_post_applications(self, chat_id, post_id):
        print(f"Viewing applications for post ID={post_id}")
        self.bot_service.send_message(chat_id, f"📋 Showing applications for post {post_id}.")

    def cancel_request(self, chat_id, request_id):
        print(f"Cancelling request ID={request_id}")
        self.bot_service.send_message(chat_id, f"❌ Request {request_id} cancelled.")

    def pay_for_completed_request(self, chat_id, request_id):
        print(f"Paying for completed request ID={request_id}")
        self.bot_service.send_message(chat_id, f"💳 Payment initiated for request {request_id}.")

    def review_completed_request(self, chat_id, request_id):
        print(f"Reviewing completed request ID={request_id}")
        self.bot_service.send_message(chat_id, f"📝 Review submitted for request {request_id}.")

    def report_completed_request(self, chat_id, request_id):
        print(f"Reporting completed request ID={request_id}")
        self.bot_service.send_message(chat_id, f"🚨 Report submitted for request {request_id}.")

    def review_canceled_request(self, chat_id, request_id):
        print(f"Reviewing canceled request ID={request_id}")
        self.bot_service.send_message(chat_id, f"📝 Review submitted for canceled request {request_id}.")

    def report_canceled_request(self, chat_id, request_id):
        print(f"Reporting canceled request ID={request_id}")
        self.bot_service.send_message(chat_id, f"🚨 Report submitted for canceled request {request_id}.")
