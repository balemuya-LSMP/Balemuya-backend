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
            'text':text
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup  
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
    
    def send_document(self, chat_id, document, filename):
        url = f"{self.base_url}/sendDocument"
        files = {
            'document': (filename, document)
        }
        payload = {
            "chat_id": chat_id,
        }
        response = requests.post(url, data=payload, files=files)
        return response
            
    def send_photo(self, chat_id, photo_url):
        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_url
        }
        response = requests.post(url, json=payload)
        return response.json()