import requests
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.core.mail import send_mail

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
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

from urllib.parse import parse_qs

from users.models import User, Professional, Customer, Admin, Payment, SubscriptionPlan,VerificationRequest
from users.utils import send_sms, generate_otp,send_push_notification
from notifications.models import Notification

from users.serializers import UserSerializer, LoginSerializer, ProfessionalSerializer, CustomerSerializer, AdminSerializer,\
  VerificationRequestSerializer
from notifications.serializers import NotificationSerializer

# Create your views here.

class ProfessionalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("You are not authorized to access this.")
        
        queryset = Professional.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'verified':
                queryset = queryset.filter(is_verified=True)
            elif status_filter == 'available':
                queryset = queryset.filter(is_available=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter is None:
                status_filter = ''
            return Response({"message": f"No {status_filter} professionals found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




# View for listing Customers
class CustomerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("You are not authorized to access this.")
        
        queryset = Customer.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter ==None:
                status_filter = ''
            return Response({"message": f"No {status_filter} customers found."}, status=404)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# View for listing Admins
class AdminListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminSerializer

    def get_queryset(self):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied({"message":
                "You are not authorized to access this."})
        queryset = Admin.objects.all()
        status_filter = self.request.query_params.get('status', None)

        if status_filter:
            if status_filter == 'active':
                queryset = queryset.filter(user__is_active=True)
            elif status_filter == 'blocked':
                queryset = queryset.filter(user__is_blocked=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = self.request.query_params.get('status', None)

        if not queryset.exists():
            if status_filter ==None:
                status_filter = ''
            return Response({"message": f"No {status_filter} Admin found."}, status=404)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
class AdminVerifyProfessionalView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        try:
            verification_request = VerificationRequest.objects.get(id=pk)
        except VerificationRequest.DoesNotExist:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        if verification_request.status != "pending":
            return Response({"error": "This request has already been processed."}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get("action")
        admin_comment = request.data.get("admin_comment", "")

        if action not in ["approved", "rejected"]:
            return Response({"error": "Invalid action. Must be 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the verification request
        verification_request.status = action
        verification_request.admin_comment = admin_comment
        verification_request.verified_by = request.user.admin 
        verification_request.save()
        
        if verification_request.status == "approved":
            professional = verification_request.professional
            professional.is_verified = True
            professional.save()
            
            subject = "Verification Approved"
            message = "Congratulations! Your verification request has been approved by the admin."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [professional.user.email]
            send_mail(subject, message, email_from, recipient_list)
            # send_push_notification(professional.user, "Congratulations! Your verification request has been approved by the admin.")

        elif verification_request.status == "rejected":
            subject = "Verification Rejected"
            message = f"Your verification request has been rejected by the admin. Reason: {admin_comment}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [verification_request.professional.user.email]
            send_mail(subject, message, email_from, recipient_list)
            # send_push_notification(verification_request.professional.user, f"Your verification request has been rejected by the admin. Reason: {admin_comment}")
            
        serializer = VerificationRequestSerializer(verification_request)
        return Response({"message": f"Request successfully {action}.", "data": serializer.data}, status=status.HTTP_200_OK)
    
class ProfessionalVerificationRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            verification_requests = VerificationRequest.objects.filter(status='pending')
        except VerificationRequest.DoesNotExist:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VerificationRequestSerializer(verification_requests, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    