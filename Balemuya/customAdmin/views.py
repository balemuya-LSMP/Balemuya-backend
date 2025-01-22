import requests
import json
from django.core.cache import cache
from django.contrib.auth import login

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

from users.models import User, Professional, Customer, Admin
from users.utils import send_sms, generate_otp, send_email_confirmation

from users.serializers import UserSerializer, LoginSerializer, ProfessionalSerializer, CustomerSerializer, AdminSerializer

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


class VerifyProfessional(APIView):
    pass


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