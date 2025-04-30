# services.py
import requests
import re
from django.conf import settings
from django.core.cache import cache

class TelegramAuthService:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def set_user_state(self, state):
        cache.set(f"user_state_{self.chat_id}", state, timeout=3600)

    def get_user_state(self):
        return cache.get(f"user_state_{self.chat_id}")

    def set_session_data(self, key, value):
        cache.set(f"user_{key}_{self.chat_id}", value, timeout=3600)

    def get_session_data(self, key):
        return cache.get(f"user_{key}_{self.chat_id}")

    def clear_session(self):
        keys = ["state", "email", "username", "phone", "user_type", "entity_type"]
        for key in keys:
            cache.delete(f"user_{key}_{self.chat_id}")

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def send_registration_request(self, data):
        try:
            url = f"{settings.BACKEND_URL}users/auth/register/"
            response = requests.post(url, data=data)
            if response.status_code == 201:
                return {"status": "success"}
            return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}

    def send_login_request(self, email, password):
        try:
            url = f"{settings.BACKEND_URL}users/auth/login/"
            response = requests.post(url, data={"email": email, "password": password})
            print('login response is ',response)
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access")
                refresh_token = data.get("refresh")
                if access_token and refresh_token:
                    cache.set(f"user_access_token_{self.chat_id}", access_token, timeout=3600)  # usually short-lived
                    cache.set(f"user_refresh_token_{self.chat_id}", refresh_token, timeout=7 * 24 * 3600)  # longer-lived
                    print('success is returned')
                    return {"status": "success"}
            return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}
    
    def get_access_token(self):
        return cache.get(f"user_access_token_{self.chat_id}")

    def get_refresh_token(self):
        return cache.get(f"user_refresh_token_{self.chat_id}")


class TelegramBotService:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text, reply_markup=None):
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
