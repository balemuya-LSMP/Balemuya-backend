import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        token = self.get_token_from_query_string()
        if not token:
            return await self.reject_connection("Unauthorized: Missing token.")

        self.user = await self.authenticate_user(token)
        if not self.user:
            return await self.reject_connection("Unauthorized: Invalid or missing token.")

        # Get group names based on user type
        self.group_names = await self.get_group_names_by_user_type(self.user)

        # Add the user to each group
        for group_name in self.group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)

        print(f'User connected to groups: {self.group_names}')
        await self.send(text_data=json.dumps({
            "message": f"Connected to groups: {self.group_names}"
        }))

    async def disconnect(self, close_code):
        # Remove the user from each group
        for group_name in self.group_names:
            await self.channel_layer.group_discard(group_name, self.channel_name)

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
        except Exception:
            return None

    @database_sync_to_async
    def get_group_names_by_user_type(self, user):
        group_names = []
        if user.user_type == 'professional':
            group_names.append(f"professional_{user.id}_subscription_notifications")
            group_names.append(f"professional_{application_acepted}_notifications")
            group_names.append("professional_general_notifications")
            for category in user.professional.categories.all():  
                group_names.append(f"professional_{user.id}_new_jobs")

        elif user.user_type == 'customer':
            group_names.append(f"customer_{user.id}_service_application_requests")
            group_names.append("customer_general_notifications")

        elif user.user_type == 'admin':
            group_names.append("admin_verification_notifications")
            group_names.append("admin_booking_complain_notifications")
            group_names.append("admin_feedback_notifications")
            group_names.append("admin_notifications")
            group_names.append("admin_general_notifications")

        return group_names

    async def reject_connection(self, message):
        await self.send(text_data=json.dumps({"error": message}))
        await self.close(code=4000)

    async def send_notification(self, event):
        notification = event['message']
        await self.send(text_data=json.dumps({
            'notification': notification
        }))