from django.conf import settings
from django_twilio.client import twilio_client
from django.http import JsonResponse
import random

@staticmethod
def generate_otp():
        """Generates a 6-digit random OTP."""
        return random.randint(100000, 999999)
    

def send_sms(request,to,message_body):
    try:
        sender_number = settings.TWILIO_DEFAULT_CALLERID
        if not sender_number:
            return JsonResponse({"error": "Twilio sender number is not configured in settings."})

        message = twilio_client.messages.create(
            body=message_body,
            from_=sender_number,
            to=to
        )
        print('message is sent ',message,'to',to,'from','sender',sender_number)
        return JsonResponse({"message": f"Message sent: {message.sid}"})
    except Exception as e:
        return JsonResponse({"error": str(e)})
