import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection. Authenticates the user via a JWT token 
        and assigns the appropriate group based on the URL parameters.
        """
        # Accept the connection initially
        await self.accept()

        # Parse the token from the query string
        token = self.get_token_from_query_string()
        if not token:
            return await self.reject_connection("Unauthorized: Missing token.")

        # Authenticate the user using the token
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            self.user = await self.get_user(user_id)
        except get_user_model().DoesNotExist:
            return await self.reject_connection("Unauthorized: User not found.")
        except Exception as e:
            return await self.reject_connection(f"Unauthorized: Invalid token. Error: {str(e)}")

        # Ensure the user is authenticated
        if not self.user.is_authenticated:
            return await self.reject_connection("Unauthorized: Invalid or missing token.")

        # Assign the user to a group based on the URL path
        self.group_name = self.get_group_name()
        if not self.group_name:
            return await self.reject_connection("Invalid group name.")

        # Add the user to the group and notify of successful connection
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "message": f"Connected to group: {self.group_name}."
        }))

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection by removing the user from the group.
        """
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handles incoming WebSocket messages (if needed).
        """
        try:
            data = json.loads(text_data)
            await self.send(text_data=json.dumps({
                "message": f"Echo: {data.get('message', 'No message provided')}"
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format."
            }))

    async def send_notification(self, event):
        """
        Sends notifications to the WebSocket client.
        """
        notification = event.get("message", {})
        await self.send(text_data=json.dumps(notification))

    def get_token_from_query_string(self):
        """
        Extracts the JWT token from the query string.
        """
        query_string = self.scope["query_string"].decode("utf-8")
        if "token=" in query_string:
            return query_string.split("token=")[-1]
        return None

    def get_group_name(self):
        """
        Determines the group name based on the URL path and parameters.
        """
        user_id = self.scope["url_route"]["kwargs"].get("user_id")
        category = self.scope["url_route"]["kwargs"].get("category")
        customer_id = self.scope["url_route"]["kwargs"].get("customer_id")
        professional_id = self.scope["url_route"]["kwargs"].get("professional_id")

        if user_id:
            return f"user_{user_id}"
        elif "service-post" in self.scope["path"] and category:
            return f"category_{category}"
        elif "application" in self.scope["path"] and customer_id:
            return f"customer_{customer_id}"
        elif "application-status" in self.scope["path"] and professional_id:
            return f"professional_{professional_id}"
        return None

    async def reject_connection(self, message):
        """
        Sends an error message to the client and closes the WebSocket connection.
        """
        await self.send(text_data=json.dumps({"error": message}))
        await self.close(code=4000)

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Fetches the user from the database asynchronously.
        """
        User = get_user_model()
        return User.objects.get(id=user_id)
