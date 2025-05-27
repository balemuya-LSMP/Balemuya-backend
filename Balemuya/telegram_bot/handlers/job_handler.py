from users.models import User
import requests
from django.conf import settings
from datetime import datetime

class JobHandler:
    def __init__(self, facade):
        self.facade = facade

    def handle(self, message, user_state):
        chat_id = self.facade.chat_id
        auth = self.facade.auth_service
        bot = self.facade.bot_service

        # Handle initial command
        if message == "🆕 Post New Job":
            self.ask_for_job_title(auth, bot)
            return

        # Handle based on user state
        if user_state == "waiting_for_job_title":
            self.process_job_title(message, auth, bot)

        elif user_state == "waiting_for_job_description":
            self.process_job_description(message, auth, bot)

        elif user_state == "waiting_for_job_category":
            self.process_job_category(message, auth, bot)

        elif user_state == "waiting_for_job_urgency":
            self.process_job_urgency(message, auth, bot)

        elif user_state == "waiting_for_location":
            # Location should be a dict-like object with `.location.latitude` and `.location.longitude`
            if hasattr(message, 'location'):
                self.process_location(message, auth, bot)
            else:
                bot.send_message(chat_id, "⚠️ Please send your location using the button below.")
                self.ask_for_location(auth, bot)

        elif user_state == "waiting_for_work_due_date":
            self.process_work_due_date(message, auth, bot)

    def ask_for_job_title(self, auth, bot):
        bot.send_message(auth.chat_id, "📄 Please enter the job title:")
        auth.set_user_state("waiting_for_job_title")

    def process_job_title(self, text, auth, bot):
        auth.set_session_data("job_title", text.strip())
        self.ask_for_job_description(auth, bot)

    def ask_for_job_description(self, auth, bot):
        bot.send_message(auth.chat_id, "📝 Please enter the job description:")
        auth.set_user_state("waiting_for_job_description")

    def process_job_description(self, text, auth, bot):
        auth.set_session_data("job_description", text.strip())
        self.ask_for_job_category(auth, bot)

    def ask_for_job_category(self, auth, bot):
        bot.send_message(auth.chat_id, "🏷️ Please enter the job category:")
        auth.set_user_state("waiting_for_job_category")

    def process_job_category(self, text, auth, bot):
        auth.set_session_data("job_category", text.strip())
        self.ask_for_job_urgency(auth, bot)

    def ask_for_job_urgency(self, auth, bot):
        bot.send_message(auth.chat_id, "⚡ Please enter the job urgency (urgent/normal):")
        auth.set_user_state("waiting_for_job_urgency")

    def process_job_urgency(self, text, auth, bot):
        urgency = text.strip().lower()
        if urgency not in ["urgent", "normal"]:
            bot.send_message(auth.chat_id, "⚠️ Please enter *urgent* or *normal* only.")
            return
        auth.set_session_data("urgency", urgency)
        self.ask_for_location(auth, bot)

    def ask_for_location(self, auth, bot):
        keyboard = [[{
            "text": "📍 Send Location",
            "request_location": True
        }]]
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        bot.send_message(auth.chat_id, "📍 Please share your location:", reply_markup=reply_markup)
        auth.set_user_state("waiting_for_location")

    def process_location(self, message, auth, bot):
        print('location message is', message)
        latitude = message.location.latitude
        longitude = message.location.longitude

        location_data = {
            'latitude': latitude,
            'longitude': longitude
        }
        auth.set_session_data("location", location_data)
        self.ask_for_work_due_date(auth, bot)

    def ask_for_work_due_date(self, auth, bot):
        bot.send_message(auth.chat_id, "📅 Please enter the work due date (YYYY-MM-DD):")
        auth.set_user_state("waiting_for_work_due_date")

    def process_work_due_date(self, text, auth, bot):
        try:
            work_due_date = datetime.strptime(text.strip(), "%Y-%m-%d")
            auth.set_session_data("work_due_date", work_due_date.isoformat())
        except ValueError:
            bot.send_message(auth.chat_id, "⚠️ Invalid date format. Use YYYY-MM-DD.")
            return

        job_data = {
            'title': auth.get_session_data("job_title"),
            'description': auth.get_session_data("job_description"),
            'category': auth.get_session_data("job_category"),
            'urgency': auth.get_session_data("urgency"),
            'work_due_date': auth.get_session_data("work_due_date"),
            'location': auth.get_session_data("location")
        }

        print('job payload data', job_data)
        self.create_job_post(job_data, bot)

        auth.clear_session()
        auth.set_user_state(None)

    def create_job_post(self, job_data, bot):
        access_token = self.facade.auth_service.get_access_token()
        if not access_token:
            bot.send_message(self.facade.chat_id, "⚠️ Authorization failed. Please login again.")
            return

        url = f"{settings.BACKEND_URL}services/service-posts/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=job_data, headers=headers)
            print('response of create job is', response)
            print('status of create job is', response.status_code)

            if response.status_code == 201:
                bot.send_message(self.facade.chat_id, "✅ Job post created successfully!")
            else:
                print("Failed to create post:", response.text)
                bot.send_message(self.facade.chat_id, "⚠️ Failed to create job post.")
        except requests.exceptions.RequestException as e:
            print(f"Error creating job post: {e}")
            bot.send_message(self.facade.chat_id, "⚠️ An error occurred while creating the job post.")
