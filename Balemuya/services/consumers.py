import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the token from the query string or headers (depending on your frontend setup)
        token = self.scope['query_params'].get('token')  # or you can get from headers

        if token:
            try:
                # Validate the JWT token
                access_token = AccessToken(token)
                user = access_token.user  # Get the user from the token
                self.user = user
            except Exception as e:
                raise AuthenticationFailed("Invalid token")

        else:
            self.user = AnonymousUser()

        # Permission check: only authenticated users can connect
        if self.user.is_authenticated:
            if "service-post" in self.scope["path"]:
                category = self.scope["url_route"]["kwargs"]["category"]
                self.group_name = f"category_{category}"
                print(f"Connecting to service-post group: {self.group_name}")
            elif "application" in self.scope["path"]:
                customer_id = self.scope["url_route"]["kwargs"].get("customer_id")
                self.group_name = f"customer_{customer_id}"
                print(f"Connecting to application group: {self.group_name}")
            elif "application-status" in self.scope["path"]:
                professional_id = self.scope["url_route"]["kwargs"].get("professional_id")
                self.group_name = f"professional_{professional_id}"
                print(f"Connecting to application-status group: {self.group_name}")
            else:
                self.group_name = None
                print("Invalid group name.")

            if self.group_name is not None:
                # Join the group
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.accept()
                await self.send(text_data=json.dumps({
                    'message': f'Connected to group: {self.group_name}.'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'message': 'Invalid group name.'
                }))
                await self.close(code=4001)
        else:
            await self.send(text_data=json.dumps({
                'message': 'Unauthorized: Invalid or missing token.'
            }))
            await self.close(code=4000)

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket is closed
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message,
        }))
