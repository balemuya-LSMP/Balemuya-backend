import requests
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.core.mail import send_mail
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

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
from services.models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain
from users.models import User, Professional, Customer, Admin, Payment, SubscriptionPlan,VerificationRequest,Feedback
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
        
        if verification_requests.count() == 0:
            return Response({"error": "No verification requests found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = VerificationRequestSerializer(verification_requests, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    

class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        # User Statistics
        user_statistics = {
            "total_users": User.objects.filter(is_active=True).count(),
            "total_professionals": Professional.objects.filter(user__is_active=True).count(),
            "total_customers": Customer.objects.filter(user__is_active=True).count(),
            "total_admins": Admin.objects.filter(user__is_active=True).count(),
            "blocked_users": User.objects.filter(is_blocked=True).count(),
            "blocked_professionals": Professional.objects.filter(user__is_blocked=True).count(),
            "blocked_customers": Customer.objects.filter(user__is_blocked=True).count(),
            "blocked_admins": Admin.objects.filter(user__is_blocked=True).count(),
            "verified_professionals": Professional.objects.filter(is_verified=True).count(),
            "available_professionals": Professional.objects.filter(is_available=True).count(),
        }

        # Service Statistics
        service_statistics = {
            "total_services": ServicePost.objects.count(),
            "completed_services": ServicePost.objects.filter(status='completed').count(),
            "booked_services": ServicePost.objects.filter(status='booked').count(),
            "active_services": ServicePost.objects.filter(status='active').count(),
        }

        # Booking Statistics
        booking_statistics = {
            "total_bookings": ServiceBooking.objects.count(),
            "pending_bookings": ServiceBooking.objects.filter(status='pending').count(),
            "completed_bookings": ServiceBooking.objects.filter(status='completed').count(),
            "canceled_bookings": ServiceBooking.objects.filter(status='canceled').count(),
        }

        # Feedback and Complaint Statistics
        feedback_statistics = {
            "total_feedbacks": Feedback.objects.count(),
            "total_complains": Complain.objects.count(),
            "resolved_complains": Complain.objects.filter(status=True).count(),
            "unresolved_complains": Complain.objects.filter(status=False).count(),
        }

        # Financial Statistics
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue_stats = (
            Payment.objects
            .filter(payment_status='completed')
            .annotate(month=TruncMonth('payment_date'))
            .values('month')
            .annotate(
                total_revenue=Sum('amount'), 
                payment_count=Count('id')
            )
            .order_by('month')
        )
        monthly_revenue_stats_list = list(monthly_revenue_stats)
        
        monthly_subscription_plan_stats = (
                SubscriptionPlan.objects
                .annotate(month=TruncMonth('start_date'))  
                .values('month')
                .annotate(plan_count=Count('id'))
                .order_by('month')
            )

        monthly_subscription_plan_stats_list = list(monthly_subscription_plan_stats)
        number_of_gold_subscribers = SubscriptionPlan.objects.filter(plan_type='gold').count()
        number_of_dimond_subscribers = SubscriptionPlan.objects.filter(plan_type='dimond').count()
        number_of_silver_subscribers = SubscriptionPlan.objects.filter(plan_type='silver').count()

        # User Join Statistics
        monthly_user_stats = (
            User.objects
            .annotate(month=TruncMonth('date_joined'))
            .values('month')
            .annotate(user_count=Count('id'))
            .order_by('month')
        )
        monthly_user_stats_list = list(monthly_user_stats)
        

        # Prepare the final response
        response_data = {
            "user_statistics": user_statistics,
            "service_statistics": service_statistics,
            "booking_statistics": booking_statistics,
            "feedback_statistics": feedback_statistics,
            "financial_statistics": {
                "total_revenue": total_revenue,
                "number_of_gold_subscribers":number_of_gold_subscribers,
                "number_of_dimond_subscribers":number_of_dimond_subscribers,
                "number_of_silver_subscribers":number_of_silver_subscribers,
                "monthly_revenue_stats": monthly_revenue_stats_list,
                "monthly_subscription_plan_stats_list":monthly_subscription_plan_stats_list
            },
            "monthly_user_stats": monthly_user_stats_list,
        }

        return Response(response_data, status=status.HTTP_200_OK)         
         
     
         
    
    
    
