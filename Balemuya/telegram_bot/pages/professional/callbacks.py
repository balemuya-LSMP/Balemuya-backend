import requests
from django.conf import settings

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
        else:
            self.bot_service.send_message(chat_id, "⚠️ Unknown action.")

    def extract_service_post_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None

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
            print('application response is Response:', response.json())  # Log response for debugging
            if response.status_code == 201:
                self.bot_service.send_message(chat_id, "✅ Your application has been submitted successfully!")
            else:
                self.bot_service.send_message(chat_id, "❌ Failed to submit your application. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error processing application: {e}")
            self.bot_service.send_message(chat_id, "⚠️ An error occurred while processing your application.")