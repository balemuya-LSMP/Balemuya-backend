from uuid import UUID
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Extract the token
        token = self.get_token_from_query_string()
        if not token:
            return await self.reject_connection("Unauthorized: Missing token.")

        # Authenticate the user
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            self.user = await self.get_user(user_id)
        except get_user_model().DoesNotExist:
            return await self.reject_connection("Unauthorized: User not found.")
        except Exception as e:
            return await self.reject_connection(f"Unauthorized: Invalid token. Error: {str(e)}")

        if not self.user.is_authenticated:
            return await self.reject_connection("Unauthorized: Invalid or missing token.")

        # Determine the group name based on the URL
        self.group_name = self.get_group_name()
        if not self.group_name:
            return await self.reject_connection("Invalid group name.")

        # Add the user to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "message": f"Connected to group: {self.group_name}."
        }))

    def get_token_from_query_string(self):
        query_string = self.scope["query_string"].decode("utf-8")
        return query_string.split("token=")[-1] if "token=" in query_string else None

    def get_group_name(self):
        user_id = self.scope["url_route"]["kwargs"].get("user_id")
        category = self.scope["url_route"]["kwargs"].get("category")
        customer_id = self.scope["url_route"]["kwargs"].get("customer_id")
        professional_id = self.scope["url_route"]["kwargs"].get("professional_id")

        if user_id:
            return f"user_{user_id}"
        elif category:
            return f"category_{category}"
        elif customer_id:
            return f"customer_{customer_id}"
        elif professional_id:
            return f"professional_{professional_id}"
        return None

    async def reject_connection(self, message):
        await self.send(text_data=json.dumps({"error": message}))
        await self.close(code=4000)

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        return User.objects.get(id=user_id)
