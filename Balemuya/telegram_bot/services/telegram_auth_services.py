import requests
import re
from django.core.cache import cache
from django.conf import settings

class TelegramAuthService:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.user_instance = None
        if self.user_instance is None:
            self.get_logged_in_user()
    
    def get_user_type(self):
        if self.user_instance:
            return self.user_instance['user']['user_type']
        return None
            

    def set_user_state(self, state):
        cache.set(f"user_state_{self.chat_id}", state)
        
    def set_menu_state(self, state):
        cache.set(f"menu_state_{self.chat_id}", state)

    def get_menu_state(self):
        return cache.get(f"menu_state_{self.chat_id}")
    def get_user_state(self):
        return cache.get(f"user_state_{self.chat_id}")

    def set_session_data(self, key, value):
        cache.set(f'user_session_{self.chat_id}_{key}', value)
        
    def get_session_data(self, key):
        return cache.get(f'user_session_{self.chat_id}_{key}')
    
    def clear_session(self):
        cache.delete(f"user_state_{self.chat_id}")

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
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("user")['access']
                refresh_token = data.get("user")['refresh']
                user_type = data.get('user')['user_type']

                if access_token and refresh_token:
                    cache.set(f"user_access_token_{self.chat_id}", access_token, timeout=3600)  # short-lived
                    cache.set(f"user_refresh_token_{self.chat_id}", refresh_token, timeout=7 * 24 * 3600)  # longer-lived
                    self.get_logged_in_user()
                    
                    return {"status": "success", "user_type": user_type,"user":self.user_instance}
            return {"status": "failure", "message": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}
    
    def logout_user(self):
        if self.user_instance:
            id=self.user_instance['user']['id']
            user = User.objects.filter(id=id,telegram_chat_id=self.chat_id).first()
            if user:
                user.telegram_chat_id=None
                user.save()
                return True
            return False
        else:
            self.get_logged_in_user()
        
        

    def get_logged_in_user(self):
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"status": "failure", "message": "Access token not found in cache."}

            url = f"{settings.BACKEND_URL}users/profile/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.user_instance = data.get("user")
                
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": str(e)}

    def get_access_token(self):
        return cache.get(f"user_access_token_{self.chat_id}")

    def get_refresh_token(self):
        return cache.get(f"user_refresh_token_{self.chat_id}")