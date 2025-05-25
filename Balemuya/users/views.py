import requests
import uuid
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.db import transaction
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.conf import settings

from allauth.account.models import get_adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.models import SocialApp

# from fcm_django.models import FCMDevice

from urllib.parse import parse_qs

from .models import User,Professional, Customer, Admin,Payment,SubscriptionPlan,Payment,Skill,Education,Portfolio,Certificate,Address,VerificationRequest,\
    Feedback,Favorite
from common.models import Category
from .utils import send_sms, generate_otp, send_email_confirmation,notify_user

from .serializers import  LoginSerializer ,ProfessionalSerializer,CustomerSerializer, AdminSerializer,\
    VerificationRequestSerializer,PortfolioSerializer,CertificateSerializer,EducationSerializer,SkillSerializer,PaymentSerializer,SubscriptionPlanSerializer,\
        FeedbackSerializer,FeedbackDetailSerializer,FavoriteSerializer,FavoriteDetailSerializer
    
from common.serializers import UserSerializer, AddressSerializer,CategorySerializer
from .professional.utils import check_professional_subscription
from .pagination import CustomPagination
class RegisterFCMDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        device_type = request.data.get("type") 

        if token:
            device, created = FCMDevice.objects.update_or_create(
                user=request.user, 
                registration_id=token,
                defaults={"type": device_type}
            )
            return Response({"message": "Device registered successfully."})
        return Response({"error": "Token is required."}, status=400)


class RegisterView(APIView):
    serializer_class = UserSerializer
    
    def post(self, request, *args, **kwargs):
        serializer_class = self.serializer_class
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user_instance = serializer.save()
            token = default_token_generator.make_token(user_instance)
            uid = urlsafe_base64_encode(str(user_instance.pk).encode())
            
            current_domain = request.get_host()
            verification_link = f'http://{current_domain}/api/users/auth/verify-email/?uid={uid}&token={token}'
            
            subject = 'Verify your email for Balemuya.'
            message = f'Please click the link below to verify your email for Balemuya.\n\n{verification_link}'
            recipient_list = [user_instance.email]
            print('user instance  is',user_instance)
            
            # send confirmation email
            print('email send start')
            send_email_confirmation(subject, message, recipient_list)
            print('email send end')
            
            otp = generate_otp()
            cache.set(f"otp_{user_instance.email}", otp, timeout=300)
            
            cached = cache.get(f"otp_{user_instance.email}")
            print('cached otp', cached)
        
            phone_number = user_instance.phone_number
            message_body = f"Hello {user_instance.username}, your OTP is {otp}. It is only valid for 5 minutes."
            send_sms(request, to=phone_number, message_body=message_body)
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.is_active = True
            user.save()

            html_content = render_to_string('email_verification_success.html', {
                "message": f"{user.user_type} Email is verified successfully!",
                "user": user,
            })
            return HttpResponse(html_content, status=200, content_type="text/html")
        else:
            html_content = render_to_string('email_verification_failed.html', {
                "message": "Invalid or expired token.",
            })
            return HttpResponse(html_content, status=400, content_type="text/html")


class VerifyPhoneView(APIView):
    
    def post(self, request):
        otp = int(request.data.get('otp'))
        email = request.data.get('email')
        cached_otp = cache.get(f"otp_{email}")
        
        if cached_otp == otp:
            print('otp is valid')
            user = User.objects.filter(email=email).first()
            user.is_phone_verified = True
            user.is_active = True
            user.save()
            cache.delete(f"otp_{email}")
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP, please type again.'}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        contact_type = request.data.get('type')  # 'email' or 'phone'
        contact_value = request.data.get('contact')  # Email address or phone number

        if not contact_type or not contact_value:
            return Response({"detail": "Type and contact are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_instance = User.objects.get(**{f"{contact_type}__iexact": contact_value})
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new OTP
        otp = get_random_string(length=6, allowed_chars='0123456789')
        cache.set(f"otp_{user_instance.id}", otp, timeout=300)  # Cache OTP for 5 minutes

        # Email verification link
        token = default_token_generator.make_token(user_instance)
        uid = urlsafe_base64_encode(str(user_instance.pk).encode())
        current_domain = request.get_host()
        verification_link = f'http://{current_domain}/api/users/auth/verify-{contact_type}/?uid={uid}&token={token}'

        # Prepare email
        subject = 'Verify your email for Balemuya.'
        message = f'Please click the link below to verify your email for Balemuya.\n\n{verification_link}'
        recipient_list = [user_instance.email]

        # Send confirmation email
        print('Email send start')
        send_email_confirmation(subject, message, recipient_list)
        print('Email send end')

        # Send OTP via SMS
        message_body = f"Hello {user_instance.username}, your OTP is {otp}. It is only valid for 5 minutes."
        send_sms(request, to=user_instance.phone_number, message_body=message_body)

        return Response({
            'message': f'OTP has been sent. Please check your {entity_type} for further instructions.',
            'data': {
                'email': user_instance.email,
                'phone': user_instance.phone_number
            }
        }, status=status.HTTP_200_OK)
class SetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        user = User.objects.filter(email=email).first()
        
        if user:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password set successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
        

class ResetPasswordView(APIView):
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = generate_otp()
            cache.set(f"otp_{user.email}", otp, timeout=300)
            phone_number = user.phone_number
            
            subject = 'Verify Reset Password for Balemuya.'
            message_body = f"Hello {user.username}, your Password reset  OTP is {otp}. It is only valid for 5 minutes."
            recipient_list = [user.email]

            # Send confirmation email
            print('Email send start')
            send_email_confirmation(subject, message_body, recipient_list)
            print('send email end')
            print('send sms start')
            send_sms(request, to=phone_number, message_body=message_body)
            print('send sms end')
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPasswordResetOTPView(APIView):
    
    def post(self, request, *args, **kwargs):
        otp = int(request.data.get('otp'))
        email = request.data.get('email')
        cached_otp = cache.get(f"otp_{email}")
        if cached_otp == otp:
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP, please type again.'}, status=status.HTTP_400_BAD_REQUEST)

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        password = user.password
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not check_password(old_password, password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if old_password == new_password:
            return Response({'error': 'New password should be different from old password.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=user.id)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

class VerifyPasswordResetOTPView(APIView):
    def post(self, request, *args, **kwargs):
        otp = int(request.data.get('otp'))
        email = request.data.get('email')
        cached_otp = cache.get(f"otp_{email}")
        if cached_otp == otp:
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP, please type again.'}, status=status.HTTP_400_BAD_REQUEST)


import logging
from urllib.parse import unquote


# Configure logging
logging.basicConfig(level=logging.INFO)

class GoogleLoginView(APIView):
    def post(self, request):
        code = request.data.get('code')
        entity_type = request.data.get('entity_type')
        user_type = request.data.get('user_type')
        username = request.data.get('username')

        if not code:
            logging.warning("Missing authorization code")
            return Response({'error': "Missing authorization code"}, status=status.HTTP_400_BAD_REQUEST)
        code = unquote(code)
        
        print('redirect url is',settings.GOOGLE_REDIRECT_URI)

        try:
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'redirect_uri': settings.GOOGLE_REDIRECT_URI,

                    'grant_type': 'authorization_code',
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if token_response.status_code != 200:
                logging.error("Failed to exchange code: %s", token_response.text)
                return Response({'error': 'Failed to exchange code for token'}, status=status.HTTP_400_BAD_REQUEST)

            tokens = token_response.json()
            access_token = tokens.get('access_token')

            # 2. Fetch user info from Google
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if user_info_response.status_code != 200:
                logging.error("Failed to fetch user info: %s", user_info_response.text)
                return Response({'error': 'Failed to fetch user info'}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_response.json()
            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')

            if not email:
                return Response({'error': "Email not found in Google account"}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Create or get the user
            user, created = User.objects.get_or_create(email=email, defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'entity_type': entity_type,
                'user_type': user_type,
                'username': username if entity_type == 'organization' else f"{first_name}{last_name}".lower()
            })

            if created and (not entity_type or not user_type):
                return Response({
                    'message': "Please provide 'entity_type' and 'user_type' for first-time users.",
                    'needs_info': True
                }, status=status.HTTP_400_BAD_REQUEST)

            # 4. Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'entity_type': user.entity_type,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error("Unexpected error: %s", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = User.objects.filter(email=email).first()
        
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({'error': 'Your account is not active. Please check your email or sms to verify your account.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user:
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)
            return Response({'message': 'Successfully logged in.',
                             "user": {
                                 'id': user.id,
                                 'email': user.email,
                                 'user_type': user.user_type,
                                 'entity_type': user.entity_type,
                                 'access': access,
                                 'refresh': refresh,
                             }
                            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header with Bearer token is required."}, status=status.HTTP_400_BAD_REQUEST)

            access_token = auth_header.split(' ')[1]

            user = request.user

            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                if not BlacklistedToken.objects.filter(token=token).exists():
                    BlacklistedToken.objects.create(token=token)

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if not user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.user_type == 'customer':
            customer = get_object_or_404(Customer, user=user)
            serializer = CustomerSerializer(customer)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)

        elif user.user_type == 'professional':
            professional = get_object_or_404(Professional, user=user)
            serializer = ProfessionalSerializer(professional)
            check_professional_subscription(professional)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)

        elif user.user_type == 'admin':
            admin = get_object_or_404(Admin, user=user)
            serializer = AdminSerializer(admin)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)

        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_serializer_class(self, user):
        if user.user_type == 'professional':
            return ProfessionalSerializer
        elif user.user_type == 'customer':
            return CustomerSerializer
        elif user.user_type == 'admin':
            return AdminSerializer
        return None

    def get(self, request, id=None, *args, **kwargs):
        user = self.get_user(id)
        
        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer_class = self.get_serializer_class(user)
        if serializer_class is None:
            return Response({'error': 'User type not recognized'}, status=status.HTTP_400_BAD_REQUEST)

        if user.user_type == 'professional':
            profile = Professional.objects.filter(user=user).first()
            if profile is None:
                return Response({'error': 'Professional profile not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializer_class(profile)

        elif user.user_type == 'customer':
            profile = Customer.objects.filter(user=user).first()
            if profile is None:
                return Response({'error': 'Customer profile not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializer_class(profile)

        elif user.user_type == 'admin':
            profile = Admin.objects.filter(user=user).first()
            if profile is None:
                return Response({'error': 'Admin profile not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializer_class(profile)

        return Response({
            'message': "Profile fetched successfully",
            'data': serializer.data
        }, status=status.HTTP_200_OK)
class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class UserBlockView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_blocked:
            user.is_blocked=False
            user.save()
            return Response({'message': 'User Unblocked successfully'}, status=status.HTTP_200_OK)
        
        elif not user.is_blocked:
            user.is_blocked=True
            user.save()
            return Response({'message': 'User blocked successfully'}, status=status.HTTP_200_OK)

class UserFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [] 
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        user_feedbacks = Feedback.objects.all().order_by('-created_at', '-rating')        
        paginator = CustomPagination() 
        
        if not user_feedbacks.exists():
            return Response({'count': 0, 'results': []}, status=status.HTTP_200_OK)

        paginated_feedbacks = paginator.paginate_queryset(user_feedbacks, request)
        serializer = FeedbackDetailSerializer(paginated_feedbacks, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        message = request.data.get('message')
        rating = request.data.get('rating')

        if message is None or rating is None:
            return Response({'detail': 'Message and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user_feedback = Feedback.objects.create(user=request.user, message=message, rating=rating)
        return Response({'message': 'Feedback created successfully.'}, status=status.HTTP_201_CREATED)
         
    def put(self, request):
        feedback_id = request.data.get('feedback_id')
        user_feedback = Feedback.objects.filter(id=feedback_id, user=request.user).first()

        if not user_feedback:
            return Response({'detail': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeedbackSerializer(user_feedback, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Feedback updated successfully.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FavoriteListCreateAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
        serializer = FavoriteDetailSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        professional_id = request.data.get('professional')

        if professional_id is None:
            return Response({'message': 'Professional ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            professional_user = User.objects.get(id=professional_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            professional=professional_user.professional
        )

        if created:
            return Response({'message': 'User added to favorites successfully!'}, status=status.HTTP_201_CREATED)
        else:
            # If it exists, delete it
            favorite.delete()
            return Response({'message': 'User removed from favorites.'}, status=status.HTTP_204_NO_CONTENT)
 