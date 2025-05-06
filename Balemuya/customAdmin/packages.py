# Standard libraries
import json
import requests
from urllib.parse import parse_qs

# Django
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import login, hashers, tokens
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

# Django REST framework
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# AllAuth (for social login)
from allauth.account.models import get_adapter
from allauth.socialaccount.models import SocialLogin, SocialApp
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

# App models
from services.models import (
    ServicePost, ServicePostApplication, ServiceBooking,
    Review, Complain, ServicePostReport
)
from users.models import (
    User, Professional, Customer, Admin,
    Payment, SubscriptionPlan, VerificationRequest, Feedback
)
from notifications.models import Notification
from common.models import Category

# Serializers
from services.serializers import ServicePostReportSerializer
from users.serializers import (
    LoginSerializer, ProfessionalSerializer, CustomerSerializer,
    AdminSerializer, VerificationRequestSerializer
)
from notifications.serializers import NotificationSerializer
from common.serializers import CategorySerializer, UserSerializer, AddressSerializer

# Utilities
from users.utils import send_sms, generate_otp, send_push_notification

# Custom permissions
from customAdmin.permissions import IsAdmin
