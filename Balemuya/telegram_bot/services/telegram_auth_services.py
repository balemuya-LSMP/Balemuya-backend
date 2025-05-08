import requests
import re
from django.core.cache import cache

class TelegramAuthService:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def set_user_state(self, state):
        cache.set(f"user_state_{self.chat_id}", state)

    def get_user_state(self):
        return cache.get(f"user_state_{self.chat_id}")

    def clear_session(self):
        cache.delete(f"user_state_{self.chat_id}")

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
    def send_registration_request(self, data):
        try:
            url = f"{settings.BACKEND_URL}users/auth/register/"
            response = requests.post(url, data=data)
            print('registration status code',response.status_code)
            print('registration status data',response.json())
            if response.status_code == 201:
                return {"status": "success"}
            return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}
            return re.match(email_regex, email) is not None

    def send_login_request(self, email, password):
        try:
            url = f"{settings.BACKEND_URL}users/auth/login/"
            response = requests.post(url, data={"email": email, "password": password})
            print('login response is ',response)
            print('login response status code ',response.status_code)
            print('login response data is ',response.json())
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("user")['access']
                refresh_token = data.get("user")['refresh']
                user_type=data.get('user')['user_type']
                if access_token and refresh_token:
                    cache.set(f"user_access_token_{self.chat_id}", access_token, timeout=3600)  # usually short-lived
                    cache.set(f"user_refresh_token_{self.chat_id}", refresh_token, timeout=7 * 24 * 3600)  # longer-lived
                    print('success is returned')
                    return {"status": "success"}
            return {"status": "failure", "message": response.text,"user_type":user_type}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}
        
    def get_loged_in_user(self,access_token):
        try:
            url = f"{settings.BACKEND_URL}users/profile/"
            response = requests.GET(url, data={"email": email, "password": password})
            print('login response is ',response)
            print('login response status code ',response.status_code)
            print('login response data is ',response.json())
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("user")['access']
                refresh_token = data.get("user")['refresh']
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