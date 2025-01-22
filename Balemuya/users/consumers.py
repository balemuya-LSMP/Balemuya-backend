import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.conf import settings
import requests
# from  users.models import Payment



class InitiatePaymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model
            User = get_user_model()
            token = self.scope['query_string'].decode().split('=')[1]

            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await database_sync_to_async(User.objects.get)(id=user_id)
                if user:
                    self.user = user
                    await self.accept()
                    print('connected successfully, user is', user.first_name)
                    await self.send(json.dumps({'response': 'WebSocket connected successfully.', 'user': user.first_name}))
                else:
                    await self.send(json.dumps({'error': 'Invalid or expired token.'}))
                    await self.close(code=4001)
            except Exception as e:
                error_message = str(e)
                print('Authentication failed:', error_message)

                if not self.channel_name:
                    await self.close(code=4001)
                else:
                    await self.accept()
                    await self.send(json.dumps({'error': f'Connection failed: {error_message}'}))
                    await self.close(code=4001)

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        from users.models import Payment
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "initiate_payment":
                await self.initiate_payment(data)
            elif action == "track_payment":
                await self.track_payment(data)
            else:
                await self.send(json.dumps({'error': 'Invalid action.'}))

        except json.JSONDecodeError:
            await self.send(json.dumps({'error': 'Invalid JSON format.'}))
        except Exception as e:
            await self.send(json.dumps({'error': f'An error occurred: {str(e)}'}))

    async def initiate_payment(self, data):
        amount = data.get("amount")
        email = self.user.email 
        txt_ref = data.get("txt_ref")  # Assuming user is authenticated
        print('txt_ref',txt_ref)

        if not amount:
            await self.send(json.dumps({'error': 'Amount is required.'}))
            return

        # Chapa API interaction
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        chapa_api_key = settings.CHAPA_SECRET_KEY  # Get the key from settings
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "tx_ref": txt_ref,
            "callback_url": "http://localhost:8000/api/payment/callback/",
            "return_url": "http://localhost:3000/payment/success/" 
        }
        headers = {
            "Authorization": f"Bearer {chapa_api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Make the API call
            response = requests.post(chapa_url, json=payload, headers=headers)
            print('response', response)

            if response.status_code == 200:
                print('response', response.json())
                result = response.json()
                print('transaction id is ',txt_ref)
                
                # Save transaction details in the database
                print('Before saving payment')
                await database_sync_to_async(self.save_payment)(txt_ref, amount, email)
                print('After saving payment')

                # Notify client with payment URL
                await self.send(json.dumps({
                    'response': 'Payment initiated successfully.',
                    'payment_url': result.get("data", {}).get("checkout_url"),
                    'transaction_id': txt_ref
                }))
            else:
                error_message = response.json().get("message", "Failed to initiate payment.")
                await self.send(json.dumps({'error': error_message}))

        except requests.RequestException as req_err:
            await self.send(json.dumps({'error': f'Payment request failed: {str(req_err)}'}))
        except Exception as e:
            await self.send(json.dumps({'error': f'An error occurred during payment initiation: {str(e)}'}))

    async def track_payment(self, data):
        transaction_id = data.get('transaction_id')
        
        # Fetch the latest payment status from the database
        payment_status = await sync_to_async(self.get_payment_status)(transaction_id)
        
        await self.send(json.dumps({
            'transaction_id': transaction_id,
            'payment_status': payment_status
        }))

    def save_payment(self, transaction_id, amount, email):
        from users.models import Payment,Professional,SubscriptionPlan
        # Create a new payment record in the database
        print('email',email,'transaction_id',transaction_id)
        professional = Professional.objects.get(user__email=email)
        subscription_plan = SubscriptionPlan.objects.get(professional=professional)
        payment_obj= Payment.objects.create(professional=professional,subscription=subscription_plan,transaction_id=transaction_id, amount=amount,payment_status='pending')
        payment_obj.save()
        if payment_obj:
            print('payment saved',payment_obj)

    @database_sync_to_async
    def get_payment_status(self, transaction_id):
        # Fetch the payment status from the database
        payment = Payment.objects.get(transaction_id=transaction_id)
        return payment.status

# Callback endpoint to handle Chapa's callback
from django.http import JsonResponse

def payment_callback(request):
    data = json.loads(request.body)
    transaction_id = data.get("transaction_id")
    status = data.get("status")

    # Update the payment status in the database
    sync_to_async(update_payment_status)(transaction_id, status)

    # Optionally notify users via WebSocket
    # Code to notify user about the payment status can be added here

    return JsonResponse({'status': 'success'})

@sync_to_async
def update_payment_status(transaction_id, status):
    # Update the payment status in the database
    payment = Payment.objects.get(transaction_id=transaction_id)
    payment.status = status
    payment.save()