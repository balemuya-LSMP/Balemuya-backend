import json
import httpx  # Use httpx for async HTTP requests
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class PaymentInitiateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Parse the token from the query string
        query_string = self.scope['query_string'].decode('utf-8')
        token = dict(item.split('=') for item in query_string.split('&')).get('token')

        if not token:
            await self.close()
            return

        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = User.objects.get(id=user_id)
        except (AccessToken.Error, ObjectDoesNotExist):
            await self.send(text_data=json.dumps({'error': 'Invalid or expired token.'}))
            await self.close()
            return

        self.room_group_name = "payment_initiate"
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        amount = data.get('amount')
        email = data.get('email')
        phone = data.get('phone')
        transaction_id = data.get('transaction_id')

        if not amount or not email or not phone or not transaction_id:
            await self.send(text_data=json.dumps({
                'error': 'Missing required fields (amount, email, phone, transaction_id).'
            }))
            return

        payment_url = await self.initiate_payment(amount, email, phone, transaction_id)

        if payment_url:
            await self.send(text_data=json.dumps({
                'message': 'Payment initiation successful!',
                'payment_url': payment_url,
            }))
        else:
            await self.send(text_data=json.dumps({
                'error': 'Failed to initiate payment with Chapa.'
            }))

    async def initiate_payment(self, amount, email, phone, transaction_id):
        """
        Initiates a payment with Chapa API and returns the payment URL.
        """
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}', 
        }

        # Prepare the data for the payment request
        payment_data = {
            "amount": amount,
            "currency": "ETB", 
            "email": email,  
            "phone_number": phone,  
            "transaction_id": transaction_id,  
            "callback_url": "https://your-website.com/payment/callback",
            "return_url": "https://your-website.com/payment/success",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.chapa.co/api/v1/transaction/initialize/", 
                    json=payment_data,
                    headers=headers
                )

            response_data = response.json()

            if response_data.get("status") == "success":
                return response_data.get("data").get("payment_url")
            else:
                return None

        except httpx.RequestError as e:
            return None


class PaymentConfirmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Implementation for payment confirmation
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle the confirmation details here