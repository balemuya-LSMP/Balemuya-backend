# services.py
import requests
from django.conf import settings
import re

class TelegramAuthService:
    def __init__(self, session, chat_id):
        self.session = session
        self.chat_id = chat_id

    def set_user_state(self, state):
        self.session[f"user_state_{self.chat_id}"] = state

    def get_user_state(self):
        return self.session.get(f"user_state_{self.chat_id}", None)

    def set_session_data(self, key, value):
        self.session[f"user_{key}_{self.chat_id}"] = value

    def get_session_data(self, key):
        return self.session.get(f"user_{key}_{self.chat_id}")

    def clear_session(self):
        # Clear all session data related to the user
        keys = [key for key in self.session.keys() if key.startswith(f"user_{self.chat_id}")]
        for key in keys:
            self.session.pop(key, None)

    def validate_email(self, email):
        # Simple email regex validation
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def send_registration_request(self, data):
        try:
            url = f"{settings.BACKEND_URL}users/auth/register/"
            response = requests.post(url, data=data)
            if response.status_code == 201:
                return {"status": "success"}
            else:
                return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}

    def send_login_request(self, email, password):
        try:
            url = f"{settings.BACKEND_URL}users/auth/login/"
            response = requests.post(url, data={"email": email, "password": password})
            if response.status_code == 200:
                return {"status": "success"}
            else:
                return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}

class TelegramBotService:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text, reply_markup=None):
        """
        Send a message to a Telegram user.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}
