import requests
import uuid
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.db import transaction
from django.utils import timezone
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
from django.db.models import Q


from allauth.account.models import get_adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.models import SocialApp

# from fcm_django.models import FCMDevice

from urllib.parse import parse_qs

from users.models import User, Professional,OrgProfessional,OrgCustomer, Customer, Admin,Payment,SubscriptionPlan,Payment,SubscriptionPayment,Skill,Education,Portfolio,Certificate,Address,VerificationRequest,\
    Feedback
from common.models import Category
from users.utils import send_sms, generate_otp, send_email_confirmation,notify_user
from services.models import ServicePost, ServicePostApplication, ServiceBooking,Review,ServiceRequest
from services.serializers import ServicePostSerializer, ServicePostApplicationSerializer,ServiceBookingSerializer,ReviewSerializer,ServiceRequestSerializer

from users.serializers import  LoginSerializer ,ProfessionalSerializer,OrgProfessionalSerializer,OrgCustomerSerializer, CustomerSerializer, AdminSerializer,\
    VerificationRequestSerializer,PortfolioSerializer,CertificateSerializer,EducationSerializer,SkillSerializer,PaymentSerializer,SubscriptionPlanSerializer,SubscriptionPaymentSerializer,\
        FeedbackSerializer
    
from common.serializers import UserSerializer, AddressSerializer,CategorySerializer
from .utils import filter_service_posts_by_distance

class ProfessionalProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,pk):
        try:
             user = User.objects.get(id=pk,user_type='professional')
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not user:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
        applied_jobs = ServicePostApplication.objects.filter(professional=user, status='pending')
        pending_jobs = ServiceBooking.objects.filter(application__professional=user, status='pending')
        canceled_jobs = ServiceBooking.objects.filter(application__professional=user, status='canceled')
        completed_jobs = ServiceBooking.objects.filter(application__professional=user, status='completed')
        reviews = Review.objects.filter(booking__application__professional=user).order_by('-created_at')
        
        professional_data = None
        if user.account_type =='organization':
            professional_data = OrgProfessionalSerializer(user.org_professional).data
        if user.account_type =='individual':
            professional_data=ProfessionalSerializer(user).data
        
        response_data={
            "professional":professional_data,
            "applied_jobs":ServicePostApplicationSerializer(applied_jobs,many=True).data,
            "pending_jobs":ServiceBookingSerializer(pending_jobs,many=True).data,
            "canceled_jobs":ServiceBookingSerializer(canceled_jobs,many=True).data,
            "completed_jobs":ServiceBookingSerializer(completed_jobs,many=True).data,
            "reviews":ReviewSerializer(reviews,many=True).data
            
        }
        return Response({"message":"Professional profile retrieved successfully", "data":response_data}, status=status.HTTP_200_OK)

class ProfessionalServiceListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type == "professional":
            query_param_status = request.query_params.get('status', None)
            if query_param_status is None:
                new_service_post = []
                if rerquest.user.account_type=='individual':
                    new_service_post = ServicePost.objects.filter(category__in=request.user.professional.categories.all(),status='active').order_by('-urgency','-created_at')
                if rerquest.user.account_type=='organization':
                     new_service_post = ServicePost.objects.filter(category__in=request.user.org_professional.categories.all(),status='active').order_by('-urgency','-created_at')
                new_service_post_serializer = ServicePostSerializer(new_service_post, many=True)
                return Response({"data": list(new_service_post_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'pending':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user,status='pending').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationSerializer(service_accepted, many=True)                
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'accepted':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user.professional,status='accepted').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationSerializer(service_accepted, many=True)
                
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'rejected':
                service_rejected = ServicePostApplication.objects.filter(professional=request.user,status='rejected').order_by('-created_at')
                service_rejected_serializer = ServicePostApplicationSerializer(service_rejected, many=True)
                return Response({"data": list(service_rejected_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'booked':
                service_booked = ServiceBooking.objects.filter(application__professional=request.user,status='pending').order_by('-created_at')
                service_booked_serializer = ServiceBookingSerializer(service_booked, many=True)
                
                return Response({"data": list(service_booked_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'completed':
                service_completed = ServiceBooking.objects.filter(application__professional=request.user,status='completed').order_by('-created_at')
                service_completed_serializer = ServiceBookingSerializer(service_completed, many=True)
                return Response({"data": list(service_completed_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'canceled':
                service_canceled = ServiceBooking.objects.filter(application__professional=request.user,status='canceled').order_by('-created_at')
                service_canceled_serializer = ServiceBookingSerializer(service_canceled, many=True)
                return Response({"data": list(service_canceled_serializer.data)}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid status parameter."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
           
class ProfessionalServiceRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        status_param = request.query_params.get('status')

    
        service_requests = ServiceRequest.objects.filter(professional=user).order_by('-updated_at')
        print('service requests ',service_requests)

        if status_param is not None:
            print('status param',status)
            service_requests = service_requests.filter(status=status_param).order_by('-updated_at')
        
        if service_requests:
             serializer = ServiceRequestSerializer(service_requests, many=True)
             return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail':"no service request found"},status=400)

    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        action = request.data.get('action')

        try:
            service_request = ServiceRequest.objects.get(id=request_id, professional=request.user)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        if action not in ['accept', 'reject']:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            service_request.status = 'accepted'
        elif action == 'reject':
            service_request.status = 'rejected'

        service_request.save()
        return Response({"success": f"Service request {action}ed."}, status=status.HTTP_200_OK)
            

class ProfessionalProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        professional = None
        serializer = None
        if request.user.user_type =='professional' and request.user.account_type=='individual':
            professional = request.user.professional
            serializer = ProfessionalSerializer(professional, data=request.data, partial=True)
        if request.user.user_type =='professional' and request.user.account_type=='organization':
            professional = request.user.org_professional
            serializer = OrgProfessionalSerializer(professional, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# views related to professional
class ProfessionalSkillView(APIView):
    permission_classes = [IsAuthenticated]

    def get_professional(self, user):
        if user.user_type != 'professional':
            return None
        
        if user.account_type == 'individual':
            return get_object_or_404(Professional, user=user)
        elif user.account_type == 'organization':
            return get_object_or_404(OrgProfessional, user=user)
        return None

    def post(self, request):
        professional = self.get_professional(request.user)

        if not professional:
            return Response({"detail": "User is not a professional."}, status=status.HTTP_400_BAD_REQUEST)

        skill_names = request.data.get("names", [])

        if not skill_names or not isinstance(skill_names, list):
            return Response({"detail": "A list of skill names is required."}, status=status.HTTP_400_BAD_REQUEST)

        added_skills = []
        for name in skill_names:
            skill, created = Skill.objects.get_or_create(name=name)
            professional.skills.add(skill)
            added_skills.append({"id": skill.id, "name": skill.name})

        return Response(
            {"detail": "Skills added successfully.", "skills": added_skills},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        """
        Remove a skill from the authenticated professional.
        """
        professional = self.get_professional(request.user)

        if not professional:
            return Response({"detail": "User is not a professional."}, status=status.HTTP_400_BAD_REQUEST)

        skill_id = request.data.get("id")

        if not skill_id:
            return Response({"detail": "Skill ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        skill = get_object_or_404(Skill, id=skill_id)

        professional.skills.remove(skill)

        return Response(
            {"detail": "Skill removed successfully.", "skill": {"id": skill.id, "name": skill.name}},
            status=status.HTTP_200_OK
        )
        
        
class ProfessionalCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get_professional(self, user):
        """Retrieve the appropriate professional instance based on user type and account type."""
        if user.user_type != 'professional':
            return None 

        if user.account_type == 'individual':
            return get_object_or_404(Professional, user=user)
        elif user.account_type == 'organization':
            return get_object_or_404(OrgProfessional, user=user)
        return None 

    def post(self, request):
        professional = self.get_professional(request.user)

        if not professional:
            return Response({"detail": "User is not a professional."}, status=status.HTTP_400_BAD_REQUEST)

        category_name = request.data.get("name")

        if not category_name:
            return Response({"detail": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)

        current_categories_count = professional.categories.count()
        max_categories = 3  

        if current_categories_count >= max_categories:
            return Response(
                {"detail": f"You cannot add more than {max_categories} categories."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category = get_object_or_404(Category, name=category_name)
        
        if category in professional.categories.all():
            return Response(
                {"detail": "This category is already associated with the professional."},
                status=status.HTTP_400_BAD_REQUEST
            )

        professional.categories.add(category)
        return Response(
            {"detail": "Category added successfully.", "category": category_name},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        professional = self.get_professional(request.user)

        if not professional:
            return Response({"detail": "User is not a professional."}, status=status.HTTP_400_BAD_REQUEST)

        category_name = request.data.get("name")

        if not category_name:
            return Response({"detail": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(Category, name=category_name)

        if category not in professional.categories.all():
            return Response({"detail": "This category is not associated with the professional."}, status=status.HTTP_400_BAD_REQUEST)

        professional.categories.remove(category)

        return Response(
            {"detail": "Category removed successfully."},
            status=status.HTTP_200_OK
        )

class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.account_type != 'individual':
            return Response({'detail': 'Professional account type must be individual.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user
        serializer = CertificateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to update certificates.'}, status=status.HTTP_403_FORBIDDEN)

        certificate = get_object_or_404(Certificate, id=pk, professional=request.user)

        serializer = CertificateSerializer(certificate, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to delete certificates.'}, status=status.HTTP_403_FORBIDDEN)

        certificate = get_object_or_404(Certificate, id=pk, professional=request.user)
        certificate.delete()
        return Response({"detail": "Certificate deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#education view
class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to add education.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user.professional
        serializer = EducationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to update education.'}, status=status.HTTP_403_FORBIDDEN)

        education = get_object_or_404(Education, pk=pk, professional=request.user.professional)
        serializer = EducationSerializer(education, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to delete education.'}, status=status.HTTP_403_FORBIDDEN)

        education = get_object_or_404(Education, pk=pk, professional=request.user.professional)
        education.delete()
        return Response({"detail": "Education deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
#portfolio class view
class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to add portfolio.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user.professional
        serializer = PortfolioSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to update portfolio.'}, status=status.HTTP_403_FORBIDDEN)

        portfolio = get_object_or_404(Portfolio, pk=pk, professional=request.user.professional)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.account_type != 'individual':
            return Response({'detail': 'User is not authorized to delete portfolio.'}, status=status.HTTP_403_FORBIDDEN)

        portfolio = get_object_or_404(Portfolio, pk=pk, professional=request.user.professional)
        portfolio.delete()
        return Response({"detail": "Portfolio deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProfessionalVerificationRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.user_type != 'professional':
            return Response({"detail": "You must be a professional to request verification."}, status=status.HTTP_403_FORBIDDEN)
        
        if user.account_type == 'individual':
            professional = get_object_or_404(Professional, user=user)
        elif user.account_type == 'organization':
            professional = get_object_or_404(OrgProfessional, user=user)
        else:
            return Response({"detail": "Invalid account type."}, status=status.HTTP_400_BAD_REQUEST)

        if professional.is_verified:
            return Response({"detail": "You are already verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        if VerificationRequest.objects.filter(professional=professional, status='pending').exists():
            return Response({"detail": "A pending verification request already exists."}, status=status.HTTP_400_BAD_REQUEST)

        verification_request = VerificationRequest.objects.create(professional=professional)
        serializer = VerificationRequestSerializer(verification_request)

        return Response({"message": "Verification request submitted successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)

class ProfessionalSubscriptionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type =='professional':
            subscription_history = SubscriptionPlan.objects.filter(user=request.user)
            serializer = SubscriptionPlanSerializer(subscription_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'This user is not Professional'},status=status.HTTP_401_UNAUTHORIZED)


class InitiateSubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        
        # Input validation
        amount = data.get("amount")
        plan_type = data.get("plan_type")
        duration = data.get("duration")
        return_url = data.get("return_url")
        txt_ref = uuid.uuid4()

        if not all([plan_type, duration, amount]):
            return Response({"detail": "Plan type, duration, and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check user type
        if user.account_type not in ['individual', 'organization']:
            return Response({"detail": "Invalid account type."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine the professional based on account type
        professional = None
        if user.account_type == 'individual':
            professional = Professional.objects.filter(user=user, is_verified=True).first()
        elif user.account_type == 'organization':
            professional = OrgProfessional.objects.filter(user=user, is_verified=True).first()

        if professional is None:
            return Response({"detail": "Professional not found or not verified."}, status=status.HTTP_404_NOT_FOUND)

        if professional.num_of_request > 0:
            return Response({"detail": "You cannot subscribe while you have remaining request coins."}, status=status.HTTP_400_BAD_REQUEST)

        active_subscription = SubscriptionPlan.objects.filter(
            professional=professional.user,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()

        subscription_payment = SubscriptionPayment.objects.filter(
            professional=professional.user,
            subscription_plan=active_subscription,
            payment_status='completed'
        ).first()

        if subscription_payment:
            return Response(
                {
                    "detail": "You already have an active subscription.",
                    "plan_type": active_subscription.plan_type,
                    "duration": active_subscription.duration,
                    "end_date": active_subscription.end_date.isoformat(),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if active_subscription:
            active_subscription.delete()

        # Prepare to initiate payment
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tx_ref": str(txt_ref),
            "return_url": f'{return_url}?transaction_id={txt_ref}'
        }
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(chapa_url, json=payload, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses

            result = response.json()

            # Use a transaction to ensure both objects are created successfully
            with transaction.atomic():
                subscription_plan = SubscriptionPlan.objects.create(
                    professional=professional.user,
                    plan_type=plan_type,
                    duration=duration
                )

                SubscriptionPayment.objects.create(
                    professional=professional.user,
                    transaction_id=str(txt_ref),
                    amount=amount,
                    payment_status='pending',
                    subscription_plan=subscription_plan
                )

            return Response(
                {
                    "message": "Payment initiated successfully.",
                    "data": {
                        "payment_url": result.get("data", {}).get("checkout_url"),
                        "transaction_id": str(txt_ref)
                    }
                },
                status=status.HTTP_200_OK
            )

        except requests.HTTPError as e:
            error_message = response.json().get("message", "Failed to initiate payment.")
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CheckPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        chapa_api_url = f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        }
            
        try:
            response = requests.get(chapa_api_url, headers=headers)
            response_data = response.json()
            if response.status_code == 200:
                payment.payment_status = 'completed'
                payment.save()

                professional = payment.professional
                professional.is_available = True
                
                subscription_plan = payment.subscription_plan
                if subscription_plan:
                    request_coins = subscription_plan.REQUEST_COINS[subscription_plan.plan_type]
                    total_requests = request_coins * subscription_plan.duration
                    professional.num_of_request += total_requests
                
                professional.save()
                
                payment_data = PaymentSerializer(payment).data
                
                return Response({
                    "message": "Payment status checked successfully.",
                    "data": {
                        "payment": payment_data
                    },
                    "first_name": response_data.get("data", {}).get("first_name"),
                    "last_name": response_data.get("data", {}).get("last_name"),
                    "email": response_data.get("data", {}).get("email"),
                    "amount": response_data.get("data", {}).get("amount"),
                    "currency": response_data.get("data", {}).get("currency")
                }, status=status.HTTP_200_OK)
            else:
                payment.payment_status = 'failed'
                payment.save()
                return Response(
                    {"detail": "Failed to retrieve payment status from Chapa."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ServicePostSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')        
        print('q',query)
        
        # Base query for active service posts
        service_posts = ServicePost.objects.filter(
            Q(title__icontains=query) |             
            Q(description__icontains=query) |       
            Q(category__name__icontains=query) |
            Q(location__region__icontains=query) |
            Q(urgency__icontains=query) |
            Q(location__city__icontains=query),
            status='active',
            work_due_date__lte=timezone.now()
        ).distinct() 

        user_location = request.user.address 
        if not user_location:
            return Response({"detail": "please turn on your location."}, status=status.HTTP_400_BAD_REQUEST)
        filtered_posts = filter_service_posts_by_distance(service_posts, user_location)

        serializer = ServicePostSerializer(filtered_posts, many=True)

        for i, post in enumerate(serializer.data):
            post['distance'] = filtered_posts[i].distance

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ServicePostFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        categories = request.data.get('categories', [])

        if not categories:
            return Response({"detail": "No categories provided."}, status=status.HTTP_400_BAD_REQUEST)

        service_posts = ServicePost.objects.filter(
            category__name__in=categories,
            status='active'
        ).order_by('-urgency', '-created_at').distinct()

        user_location = request.user.address 
        if not user_location:
            return Response({"detail": "please turn on your location."}, status=status.HTTP_400_BAD_REQUEST)
        filtered_posts = filter_service_posts_by_distance(service_posts, user_location)

        serializer = ServicePostSerializer(filtered_posts, many=True)

        for i, post in enumerate(serializer.data):
            post['distance'] = filtered_posts[i].distance 

        return Response(serializer.data, status=status.HTTP_200_OK)