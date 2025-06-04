import requests
import uuid
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from decimal import Decimal


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

from users.models import User, Professional, Customer, Admin,Payment,SubscriptionPlan,Payment,SubscriptionPayment,WithdrawalTransaction,Skill,Education,Portfolio,Certificate,Address,VerificationRequest,\
    Feedback,BankAccount,Bank
from common.models import Category
from users.utils import send_sms, generate_otp, send_email_confirmation,notify_user
from services.models import ServicePost, ServicePostApplication, ServiceBooking,Review,ServiceRequest
from services.serializers import ServicePostSerializer,ServicePostDetailSerializer, ServicePostApplicationSerializer,ServicePostApplicationDetailSerializer,ServiceBookingSerializer,ServiceBookingDetailSerializer,ReviewSerializer,ReviewDetailSerializer,ServiceRequestDetailSerializer,ServiceRequestSerializer

from users.serializers import  LoginSerializer ,ProfessionalSerializer, CustomerSerializer, AdminSerializer,\
    VerificationRequestSerializer,PortfolioSerializer,CertificateSerializer,EducationSerializer,SkillSerializer,PaymentSerializer,SubscriptionPlanSerializer,SubscriptionPlanDetailSerializer,SubscriptionPaymentSerializer,\
        FeedbackSerializer,BankAccountSerializer,BankSerializer,SubscriptionPaymentDetailSerializer,PaymentDetailSerializer
    
from common.serializers import UserSerializer, AddressSerializer,CategorySerializer
from .utils import filter_service_posts_by_distance

class ProfessionalProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,pk):
        try:
             user = User.objects.get(id=pk,user_type='professional')
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        professional = Professional.objects.get(user=user)
        print('professional',professional)
        if not professional:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
        applied_jobs = ServicePostApplication.objects.filter(professional=professional, status='pending')
        pending_jobs = ServiceBooking.objects.filter(application__professional=professional, status='pending')
        canceled_jobs = ServiceBooking.objects.filter(application__professional=professional, status='canceled')
        completed_jobs = ServiceBooking.objects.filter(application__professional=professional, status='completed')
        reviews = Review.objects.filter(booking__application__professional__user=user).order_by('-created_at')
        
        professional_data = ProfessionalSerializer(professional).data
        print('prof data',professional_data)
        response_data={
            "professional":professional_data,
            "applied_jobs":ServicePostApplicationDetailSerializer(applied_jobs,many=True).data,
            "pending_jobs":ServiceBookingDetailSerializer(pending_jobs,many=True).data,
            "canceled_jobs":ServiceBookingDetailSerializer(canceled_jobs,many=True).data,
            "completed_jobs":ServiceBookingDetailSerializer(completed_jobs,many=True).data,
            "reviews":ReviewDetailSerializer(reviews,many=True).data
            
        }
        return Response({"message":"Professional profile retrieved successfully", "data":response_data}, status=status.HTTP_200_OK)

class ProfessionalServiceListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type == "professional":
            query_param_status = request.query_params.get('status', None)
            if query_param_status is None:
                new_service_post = []
                applied_posts = ServicePostApplication.objects.filter(
                professional=request.user.professional
                    ).values('service')

                new_service_post = ServicePost.objects.filter(
                        category__in=request.user.professional.categories.all(),
                        status='active'
                ).exclude(id__in=Subquery(applied_posts)).order_by('-urgency', '-created_at')
                new_service_post_serializer = ServicePostDetailSerializer(new_service_post, many=True)
                return Response({"data": list(new_service_post_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'pending':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user.professional.id,status='pending').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationDetailSerializer(service_accepted, many=True)                
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'accepted':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user.professional,status='accepted').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationDetailSerializer(service_accepted, many=True)
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'rejected':
                service_rejected = ServicePostApplication.objects.filter(professional=request.user.professional,status='rejected').order_by('-created_at')
                service_rejected_serializer = ServicePostApplicationDetailSerializer(service_rejected, many=True)
                return Response({"data": list(service_rejected_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'booked':
                service_booked = ServiceBooking.objects.filter(application__professional=request.user.professional,status='pending').order_by('-created_at')
                service_booked_serializer = ServiceBookingDetailSerializer(service_booked, many=True)
                return Response({"data": list(service_booked_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'completed':
                service_completed = ServiceBooking.objects.filter(application__professional=request.user.professional,status='completed').order_by('-created_at')
                service_completed_serializer = ServiceBookingDetailSerializer(service_completed, many=True)
                return Response({"data": list(service_completed_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'canceled':
                service_canceled = ServiceBooking.objects.filter(application__professional=request.user.professional,status='canceled').order_by('-created_at')
                service_canceled_serializer = ServiceBookingDetailSerializer(service_canceled, many=True)
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
        print('status param',status_param)
        service_requests = ServiceRequest.objects.filter(professional=user.professional).order_by('-updated_at')
        print('service requests',service_requests)
        if status_param is not None:
            service_requests = service_requests.filter(status=status_param)
        else:
            service_requests = service_requests.filter(status='pending').order_by('-updated_at')
        
        serializer = ServiceRequestDetailSerializer(service_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        action = request.data.get('action')

        try:
            service_request = ServiceRequest.objects.get(id=request_id, professional=request.user.professional)
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

class ServiceRequestAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, req_id=None):
        if not req_id:
            return Response({"detail": "Request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service_request = ServiceRequest.objects.get(id=req_id, professional=request.user.professional)
            service_request.status = 'accepted'
            service_request.save()
            return Response({"success": "Service request accepted."}, status=status.HTTP_200_OK)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)
class ServiceRequestCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, req_id=None):
        if not req_id:
            return Response({"detail": "Request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service_request = ServiceRequest.objects.get(id=req_id, professional=request.user.professional,status='accepted')
            service_request.status = 'completed'
            service_request.save()
            return Response({"message": "Service request accepted."}, status=status.HTTP_200_OK)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

class ServiceRequestRejectAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, req_id=None):
        if not req_id:
            return Response({"detail": "Request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service_request = ServiceRequest.objects.get(id=req_id, professional=request.user.professional)
            service_request.status = 'rejected'
            service_request.save()
            return Response({"success": "Service request rejected."}, status=status.HTTP_200_OK)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

class ProfessionalProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        professional = None
        serializer = None
        if request.user.user_type =='professional':
            professional = request.user.professional
            serializer = ProfessionalSerializer(professional, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':"user is not professional"},status = status.HTTP_400_BAD_REQUEST)
    
class BankListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_401_UNAUTHORIZED)
        banks = Bank.objects.all()
        serializer = BankSerializer(banks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ProfessionalBankAccountView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            bank_account = BankAccount.objects.get(professional=request.user.professional)
        except BankAccount.DoesNotExist:
            return Response({'detail': 'Bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountSerializer(bank_account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_401_UNAUTHORIZED)

        professional = request.user.professional
        if BankAccount.objects.filter(professional=professional).exists():
            return Response({'detail': 'Bank account already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Include the professional in the data for the serializer
        data = {
            **request.data,
            'professional': professional.id  # Pass the professional's ID
        }

        serializer = BankAccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            bank_account = BankAccount.objects.get(professional=request.user.professional)
        except BankAccount.DoesNotExist:
            return Response({'detail': 'Bank account not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BankAccountSerializer(bank_account, data=request.data, partial=True)
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
        return get_object_or_404(Professional, user=user)

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
            {"message": "Skills added successfully.", "skills": added_skills},
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
            {"message": "Skill removed successfully.", "skill": {"id": skill.id, "name": skill.name}},
            status=status.HTTP_200_OK
        )
        
        
class ProfessionalCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get_professional(self, user):
        """Retrieve the appropriate professional instance based on user type and account type."""
        if user.user_type != 'professional':
            return None 

        return get_object_or_404(Professional, user=user)
        

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
            {"message": "Category added successfully.", "category": category_name},
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
        
        if request.user.entity_type != 'individual':
            return Response({'detail': 'Professional account type must be individual.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user.professional
        serializer = CertificateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not authorized to update certificates.'}, status=status.HTTP_403_FORBIDDEN)

        certificate = get_object_or_404(Certificate, id=pk, professional=request.user.professional)

        serializer = CertificateSerializer(certificate, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not authorized to delete certificates.'}, status=status.HTTP_403_FORBIDDEN)

        certificate = get_object_or_404(Certificate, id=pk, professional=request.user.professional)
        certificate.delete()
        return Response({"detail": "Certificate deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#education view
class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional' or request.user.entity_type != 'individual':
            return Response({'detail': 'User is not authorized to add education.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user.professional
        serializer = EducationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.entity_type != 'individual':
            return Response({'detail': 'User is not authorized to update education.'}, status=status.HTTP_403_FORBIDDEN)

        education = get_object_or_404(Education, pk=pk, professional=request.user.professional)
        serializer = EducationSerializer(education, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if request.user.user_type != 'professional' or request.user.entity_type != 'individual':
            return Response({'detail': 'User is not authorized to delete education.'}, status=status.HTTP_403_FORBIDDEN)

        education = get_object_or_404(Education, pk=pk, professional=request.user.professional)
        education.delete()
        return Response({"detail": "Education deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
#portfolio class view
class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not authorized to add portfolio.'}, status=status.HTTP_403_FORBIDDEN)

        professional = request.user.professional
        serializer = PortfolioSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not authorized to update portfolio.'}, status=status.HTTP_403_FORBIDDEN)

        portfolio = get_object_or_404(Portfolio, pk=pk, professional=request.user.professional)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if request.user.user_type != 'professional':
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
        
        professional = get_object_or_404(Professional, user=user)
       
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
            subscription_history = SubscriptionPlan.objects.filter(professional=request.user.professional)
            serializer = SubscriptionPlanDetailSerializer(subscription_history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'This user is not Professional'},status=status.HTTP_401_UNAUTHORIZED)
class ProfessionalPaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type =='professional':
            subscription_payment_history = SubscriptionPayment.objects.filter(professional=request.user.professional).order_by('-payment_date')[:4]
            sub_payment_serializer = SubscriptionPaymentDetailSerializer(subscription_payment_history, many=True)
            
            transfer_payment = Payment.objects.filter(professional=request.user.professional).order_by('-payment_date')[:4]
            transfer_payment_serializer = PaymentDetailSerializer(transfer_payment,many=True)
            data={
                "subscription_payments":sub_payment_serializer.data,
                "transfer_payments":transfer_payment_serializer.data,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'This user is not Professional'},status=status.HTTP_401_UNAUTHORIZED)

class InitiateSubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        amount = data.get("amount")
        plan_type = data.get("plan_type")
        duration = int(data.get("duration"))
        return_url = data.get("return_url")
        txt_ref = uuid.uuid4()

        if not all([plan_type, duration, amount]):
            return Response({"detail": "Plan type, duration, and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        professional = Professional.objects.filter(user=user, is_verified=True).first()

        if not professional:
            return Response({"detail": "Professional not found or not verified."}, status=status.HTTP_404_NOT_FOUND)


        active_subscription = SubscriptionPlan.objects.filter(
            professional=professional,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if not active_subscription and professional.is_available==True:
            professional.is_available=False
            professional.num_of_request=0
            professional.save()
        
        if active_subscription and professional.num_of_request > 0:
            return Response({"detail": f"You already have  remaining {professional.num_of_request} request coins."}, status=status.HTTP_400_BAD_REQUEST)

        chapa_url = "https://api.chapa.co/v1/transaction/initialize"

        payload = {
            "amount": str(amount),
            "first_name": professional.user.first_name if professional.user.entity_type =='individual' else professional.user.org_name,
            "last_name": professional.user.last_name if professional.user.entity_type=='individual' else '',
            "mobile": professional.user.phone_number,
            "currency": "ETB",
            "email": professional.user.email,
            "tx_ref": str(txt_ref),
            "return_url": f'{return_url}?transaction_id={txt_ref}'
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(chapa_url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if not result.get("status") == "success":
                return Response({'detail': 'Payment is not initiated, please try again'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                
                active_subscription = SubscriptionPlan.objects.create(
                        professional=professional,
                        plan_type=plan_type,
                        duration=duration
                    )

                SubscriptionPayment.objects.create(
                    professional=professional,
                    transaction_id=str(txt_ref),
                    amount=amount,
                    payment_status='pending',
                    subscription_plan=active_subscription
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

        except requests.HTTPError:
            error_message = response.json().get("message", "Failed to initiate payment.")
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class CheckPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_professional(self, user):
        return Professional.objects.filter(user=user, is_verified=True).first()
        
    def get(self, request, transaction_id):
        try:
            subscription_payment = SubscriptionPayment.objects.get(transaction_id=transaction_id)
        except SubscriptionPayment.DoesNotExist:
            return Response(
                {"detail": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if subscription_payment.payment_status == 'completed':
            return Response({'detail':"This payment already verified and completed"},status=status.HTTP_400_BAD_REQUEST)

        chapa_api_url = f"https://api.chapa.co/v1/transaction/verify/{transaction_id}"
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        }
        
        try:
            response = requests.get(chapa_api_url, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                subscription_payment.payment_status = 'completed'
                subscription_payment.save()

                professional = self.get_professional(request.user)
                if professional:
                    professional.is_available = True
                    
                    subscription_plan = subscription_payment.subscription_plan
                    if subscription_plan:
                        request_coins = subscription_plan.REQUEST_COINS[subscription_plan.plan_type]
                        total_requests = request_coins * subscription_plan.duration
                        professional.num_of_request += total_requests
                    
                    professional.save()

                payment_data = SubscriptionPaymentSerializer(subscription_payment).data
                
                return Response({
                    "message": "Payment status checked successfully.",
                    "data": {
                        "payment": payment_data,
                    },
                    "first_name": response_data.get("data", {}).get("first_name"),
                    "last_name": response_data.get("data", {}).get("last_name"),
                    "email": response_data.get("data", {}).get("email"),
                    "amount": response_data.get("data", {}).get("amount"),
                    "currency": response_data.get("data", {}).get("currency")
                }, status=status.HTTP_200_OK)
            else:
                subscription_payment.payment_status = 'failed'
                subscription_payment.save()
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
        print('service posts',service_posts)

        user_location = request.user.address 
        if not user_location:
            return Response({"detail": "please turn on your location."}, status=status.HTTP_400_BAD_REQUEST)
        filtered_posts = filter_service_posts_by_distance(service_posts, user_location)

        serializer = ServicePostDetailSerializer(filtered_posts, many=True)

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



class ProfessionalPaymentWithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'professional':
            return Response({'detail': 'User is not a professional.'}, status=status.HTTP_401_UNAUTHORIZED)

        professional = request.user.professional

        if not hasattr(professional, 'bank_account'):
            return Response({'detail': 'Professional does not have a bank account linked.'}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal_amount = request.data.get('amount')

        if not withdrawal_amount:
            return Response({'detail': 'Amount is required for withdrawal.'}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal_amount = Decimal(str(withdrawal_amount))

        if professional.balance < withdrawal_amount:
            return Response({'detail': 'Insufficient balance for withdrawal.'}, status=status.HTTP_400_BAD_REQUEST)

        bank_account = professional.bank_account
        print('bank account',bank_account)

        transfer_url = "https://api.chapa.co/v1/transfers"
        payload = {
            "account_name": bank_account.account_name,
            "account_number": bank_account.account_number,
            "amount": str(withdrawal_amount),
            "currency": "ETB",  
            "reference": str(uuid.uuid4()),
            "bank_code":bank_account.bank.code,
        }
        print('payload',payload)

        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        # Make the API request to Chapa
        try:
            response = requests.post(transfer_url, json=payload, headers=headers)
            response.raise_for_status()
            transfer_data = response.json()
            print('transfer_data',transfer_data)

            if transfer_data.get('status') == 'success':
                professional.balance -= withdrawal_amount
                professional.save()

                WithdrawalTransaction.objects.create(
                    professional=professional,
                    amount=withdrawal_amount,
                    status='completed',
                    tx_ref=transfer_data['data'],
                )
                print('professional remaining amount',professional.balance)

                return Response({
                    'message': f'Withdrawal of {withdrawal_amount} has been successfully initiated and processed.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': 'Failed to process the withdrawal with Chapa.',
                    'reason': transfer_data.get('message', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({
                'detail': f'Error communicating with Chapa API: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)