# pages/customer/callback.py

class CustomerCallbackHandler:
    def __init__(self, bot_service,auth_service):
        self.bot_service = bot_service
        self.auth_service = auth_service

    def handle_callback_query(self, callback_query):
        callback_data = callback_query.data
        chat_id = callback_query.message.chat.id

        if callback_data.startswith("apply_service"):
            service_post_id = self.extract_service_post_id(callback_data)
            if service_post_id:
                self.process_application(chat_id, service_post_id)
                self.bot_service.send_message(chat_id, "✅ You have successfully applied for the service!")
            else:
                self.bot_service.send_message(chat_id, "⚠️ Could not identify the service post.")
        else:
            self.bot_service.send_message(chat_id, "⚠️ Unknown action.")

    def extract_service_post_id(self, callback_data):
        return callback_data.split('_')[2] if len(callback_data.split('_')) > 2 else None

    def process_application(self, chat_id, service_post_id):
        # Logic for processing the application
        pass