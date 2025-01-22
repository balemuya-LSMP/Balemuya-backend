import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'You are connected!',
        }))

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data):
        # Receive a message from the WebSocket and broadcast it
        data = json.loads(text_data)
        message = data.get('message', 'No message sent!')

        await self.send(text_data=json.dumps({
            'message': f'You said: {message}',
        }))
