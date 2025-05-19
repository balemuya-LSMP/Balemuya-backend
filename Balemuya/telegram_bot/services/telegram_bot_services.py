import requests
from django.conf import settings

class TelegramBotService:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print("Error sending message:", response.json())
        else:
            print("Message sent successfully:", response.json())
            
    def send_photo(self, chat_id, photo_url):
        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_url
        }
        response = requests.post(url, json=payload)
        return response.json()