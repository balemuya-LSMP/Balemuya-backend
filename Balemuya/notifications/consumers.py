from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
from uuid import UUID
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.connected = False
        await self.accept()

        token = self.get_token_from_query_string()
        if not token:
            return await self.reject_connection("Unauthorized: Missing token.")

        self.user = await self.authenticate_user(token)
        if not self.user:
            return await self.reject_connection("Unauthorized: Invalid or missing token.")

        self.connected = True
        self.group_names = await self.get_group_names_by_user_type(self.user)

        for group_name in self.group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)

        logging.info(f'User connected to groups: {self.group_names}')
        await self.send(text_data=json.dumps({
            "message": f"Connected to to socket"
        }))

    async def disconnect(self, close_code):
        if self.connected:
            if hasattr(self, "group_names"):
                try:
                    for group_name in self.group_names:
                        await self.channel_layer.group_discard(group_name, self.channel_name)
                except Exception as e:
                    logging.error(f"Error during disconnect: {e}")
            else:
                logging.info("No groups to disconnect from.")
        
        self.connected = False 

    def get_token_from_query_string(self):
        query_string = self.scope["query_string"].decode("utf-8")
        return query_string.split("token=")[-1] if "token=" in query_string else None

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = get_user_model().objects.get(id=user_id)
            return user if user.is_authenticated else None
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return None

    @database_sync_to_async
    def get_group_names_by_user_type(self, user):
        group_names = []
        
        if user.user_type == 'professional':
            group_names.append(f"professional_{user.id}_ver_notifications")
            group_names.append(f"professional_{user.id}_sub_notifications")
            group_names.append(f"professional_{user.id}_new_bookings")
            group_names.append(f"professional_{user.id}_general_notifications")
            group_names.append(f"professional_{user.id}_new_job_request")
            for category in user.professional.categories.all():  
                group_names.append(f"professional_{user.id}_new_jobs")

        elif user.user_type == 'customer':
            group_names.append(f"customer_{user.id}_job_app_requests")
            group_names.append(f"customer_{user.id}_job_request_response")
            group_names.append(f"customer_{user.id}_general_notifications")

        elif user.user_type == 'admin':
            group_names.append("admin_verification_notifications")
            group_names.append("admin_booking_complaint_notifications")
            group_names.append("admin_feedback_notifications")
            group_names.append("admin_general_notifications")

        return group_names

    async def reject_connection(self, message):
        await self.send(text_data=json.dumps({"error": message}))
        await self.close(code=4000)

    async def send_notification(self, event):
        notification = event['data']

        try:
            notification = self.convert_uuid_fields(notification)
        except Exception as e:
            logging.error(f"Error converting UUID fields: {e}")
            return

        await self.send(text_data=json.dumps({
            'notification': notification
        }))

    def convert_uuid_fields(self, data):
        if isinstance(data, dict):
            return {key: str(value) if isinstance(value, UUID) else self.convert_uuid_fields(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_uuid_fields(item) for item in data]
        return data