from django.core.cache import cache

from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from allauth.account.models import get_adapter

from .models import User
from .utils import send_sms,generate_otp,send_email_confirmation

from .serializers import ProfessionalProfileSerializer,CustomerProfileSerializer,AdminProfileSerializer
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    
    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        
        if user['user_type'] == 'professional':
            serializer_class = ProfessionalProfileSerializer
        elif user['user_type'] == 'customer':
            serializer_class = CustomerProfileSerializer
        elif user['user_type'] == 'admin':
            serializer_class = AdminProfileSerializer
        else:
            return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user_instance = serializer.save()
            token = default_token_generator.make_token(user_instance.user)
            uid = urlsafe_base64_encode(str(user_instance.user.pk).encode())
            
            current_domain = request.get_host()
            verification_link = f'http://{current_domain}/api/users/auth/verify-email/?uid={uid}&token={token}'
            
            subject = 'Verify your email for Balemuya.'
            message = f'Please click the link below to verify your email for Balemuya.\n\n{verification_link}'
            recipient_list = [user_instance.user.email]
            
            # send confirmation email
            print('email send start')
            send_email_confirmation(subject, message,recipient_list)
            print('email send end')
            
            otp = generate_otp()
            cache.set(f"otp_{user_instance.user.phone_number}", otp, timeout=300)
        
            phone_number = user_instance.user.phone_number
            message_body = f"Hello {user_instance.user.get_full_name()}, your OTP is {otp}. It is only valid for 5 minutes."
            send_sms(request, to=phone_number, message_body=message_body)
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailView(generics.GenericAPIView):
    def get(self,request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk = uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    pass

class ResendOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    pass

class SetPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    pass

class ResetPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    pass

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfessionalProfileSerializer

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)



