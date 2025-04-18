from django.conf import settings
from django.core.mail import send_mail
from django_twilio.client import twilio_client
from django.http import JsonResponse
import random

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# from fcm_django.models import FCMDevice


def generate_otp():
    """Generates a 6-digit random OTP."""
    return random.randint(100000, 999999)


def send_sms(request, to, message_body):
    try:
        sender_number = settings.TWILIO_DEFAULT_CALLERID
        if not sender_number:
            return JsonResponse({"error": "Twilio sender number is not configured."})

        message = twilio_client.messages.create(
            body=message_body,
            from_=sender_number,
            to=to
        )
        print('message is sent ', message, 'to', to, 'from', 'sender', sender_number)
        return JsonResponse({"message": f"Message sent: {message.sid}"})
    except Exception as e:
        return JsonResponse({"error": str(e)})


def send_email_confirmation(subject, message, recipient_list):
    try:
        response = send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False
        )
        print(f"Email sent response: {response}")
        return response
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return str(e)
    
    

def send_push_notification(user, title, message):
    device = None
    # devices = FCMDevice.objects.filter(user=user)
    if devices.exists():
        device = devices.first()
        device.send_message(title=title, body=message)
    else:
        print("No devices found for this user.")




def notify_user(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'send_notification',
            'message': message
        }
    )
    