from users.models import User
import requests
from django.conf import settings
from datetime import datetime

class JobHandler:
    def __init__(self, facade):
        self.facade = facade

    def handle(self, text, user_state):
        chat_id = self.facade.chat_id
        auth = self.facade.auth_service
        bot = self.facade.bot_service

        if text == "🆕 Post New Job":
            self.facade.ask_for_job_title()
            auth.set_user_state("waiting_for_job_title")

        elif user_state == "waiting_for_job_title":
            auth.set_session_data("job_title", text.strip())
            self.facade.ask_for_job_description()
            auth.set_user_state("waiting_for_job_description")

        elif user_state == "waiting_for_job_description":
            auth.set_session_data("job_description", text.strip())
            self.facade.ask_for_job_category()
            auth.set_user_state("waiting_for_job_category")

        elif user_state == "waiting_for_job_category":
            auth.set_session_data("job_category", text.strip())
            self.facade.ask_for_job_urgency()
            auth.set_user_state("waiting_for_job_urgency")

        elif user_state == "waiting_for_job_urgency":
            urgency = text.strip().lower()
            if urgency not in ["urgent", "normal"]:
                bot.send_message(chat_id, "⚠️ Please enter 'urgent' or 'normal' for urgency.")
                return
            auth.set_session_data("urgency", urgency)
            self.facade.ask_for_work_due_date()  # New prompt for due date
            auth.set_user_state("waiting_for_work_due_date")

        elif user_state == "waiting_for_work_due_date":
            try:
                work_due_date = datetime.strptime(text.strip(), "%Y-%m-%d")
                auth.set_session_data("work_due_date", work_due_date.isoformat())
            except ValueError:
                bot.send_message(chat_id, "⚠️ Please enter the due date in YYYY-MM-DD format.")
                return

            job_data = {
                'title': auth.get_session_data("job_title"),
                'description': auth.get_session_data("job_description"),
                'category': auth.get_session_data("job_category"),
                'urgency': auth.get_session_data("urgency"),
                'work_due_date': auth.get_session_data("work_due_date")
            }
            self.create_job_post(job_data)
            bot.send_message(chat_id, "✅ Your job post has been created successfully!")
            auth.clear_session()  # Clear session data after posting
            auth.set_user_state(None)  # Reset user state

    def create_job_post(self, job_data):
        access_token = self.facade.auth_service.get_access_token()
        if not access_token:
            self.facade.bot_service.send_message(self.facade.chat_id, "⚠️ Unable to create job post. Access token not found.")
            return

        url = f"{settings.BACKEND_URL}services/service-post/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=job_data, headers=headers)
            if response.status_code == 201:
                self.facade.bot_service.send_message(self.facade.chat_id, "✅ Your job post has been created successfully!")
            else:
                print("Failed to create post:", response.json())
                self.facade.bot_service.send_message(self.facade.chat_id, "⚠️ Failed to create job post. Please try again.")
        except requests.exceptions.RequestException as e:
            print(f"Error creating job post: {e}")  # Debugging line
            self.facade.bot_service.send_message(self.facade.chat_id, "⚠️ An error occurred while creating the job post.")