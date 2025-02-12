import requests
import uuid
import json
from django.core.cache import cache
from django.contrib.auth import login
from django.db import transaction
from django.utils import timezone

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

from users.models import User, Professional, Customer, Admin,Payment,SubscriptionPlan,Payment,Skill,Education,Portfolio,Certificate,Address,VerificationRequest,\
    Feedback
from common.models import Category
from users.utils import send_sms, generate_otp, send_email_confirmation,notify_user
from services.models import ServicePost, ServicePostApplication, ServiceBooking,Review,ServiceRequest
from services.serializers import ServicePostSerializer, ServicePostApplicationSerializer,ServiceBookingSerializer,ReviewSerializer,ServiceRequestSerializer

from users.serializers import  LoginSerializer ,ProfessionalSerializer, CustomerSerializer, AdminSerializer,\
    VerificationRequestSerializer,PortfolioSerializer,CertificateSerializer,EducationSerializer,SkillSerializer,PaymentSerializer,SubscriptionPlanSerializer,\
        FeedbackSerializer
    
from common.serializers import UserSerializer, AddressSerializer,CategorySerializer

class ProfessionalProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,pk):
        try:
             user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        professional = user.professional
        if not professional:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
        applied_jobs = ServicePostApplication.objects.filter(professional=professional, status='pending')
        pending_jobs = ServiceBooking.objects.filter(application__professional=professional, status='pending')
        canceled_jobs = ServiceBooking.objects.filter(application__professional=professional, status='canceled')
        completed_jobs = ServiceBooking.objects.filter(application__professional=professional, status='completed')
        reviews = Review.objects.filter(booking__application__professional=professional).order_by('-created_at')
        
        response_data={
            "professional":ProfessionalSerializer(professional).data,
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
                new_service_post = ServicePost.objects.filter(category__in=request.user.professional.categories.all(),status='active').order_by('-created_at')
                new_service_post_serializer = ServicePostSerializer(new_service_post, many=True)
                return Response({"data": list(new_service_post_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'pending':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user.professional,status='pending').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationSerializer(service_accepted, many=True)                
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'accepted':
                service_accepted = ServicePostApplication.objects.filter(professional=request.user.professional,status='accepted').order_by('-created_at')
                service_accepted_serializer = ServicePostApplicationSerializer(service_accepted, many=True)
                
                return Response({"data": list(service_accepted_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'rejected':
                service_rejected = ServicePostApplication.objects.filter(professional=request.user.professional,status='rejected').order_by('-created_at')
                service_rejected_serializer = ServicePostApplicationSerializer(service_rejected, many=True)
                return Response({"data": list(service_rejected_serializer.data)}, status=status.HTTP_200_OK)
            
            elif query_param_status == 'booked':
                service_booked = ServiceBooking.objects.filter(application__professional=request.user.professional,status='pending').order_by('-created_at')
                service_booked_serializer = ServiceBookingSerializer(service_booked, many=True)
                
                return Response({"data": list(service_booked_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'completed':
                service_completed = ServiceBooking.objects.filter(application__professional=request.user.professional,status='completed').order_by('-created_at')
                service_completed_serializer = ServiceBookingSerializer(service_completed, many=True)
                return Response({"data": list(service_completed_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'canceled':
                service_canceled = ServiceBooking.objects.filter(application__professional=request.user.professional,status='canceled').order_by('-created_at')
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

    
        service_requests = ServiceRequest.objects.filter(professional=user.professional).order_by('-updated_at')
        print('service requests ',service_requests)

        if status_param is not None:
            service_requests = service_requests.filter(status=status_param).order_by('-updated_at')
        
        if service_requests:
             serializer = ServiceRequestSerializer(service_requests, many=True)
             return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error':"no service request found"},status=400)

    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        action = request.data.get('action')

        try:
            service_request = ServiceRequest.objects.get(id=request_id, professional=request.user)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            service_request.status = 'accepted'
        elif action == 'reject':
            service_request.status = 'rejected'

        service_request.save()
        return Response({"success": f"Service request {action}ed."}, status=status.HTTP_200_OK)
            

class ProfessionalProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        professional = request.user.professional
        serializer = ProfessionalSerializer(professional, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# views related to professional
class ProfessionalSkillView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            professional = Professional.objects.get(user=request.user)
            skill_names = request.data.get("names", [])  # Accept a list of skill names

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
        except Professional.DoesNotExist:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        """
        Remove a skill from the authenticated professional.
        """
        try:
            professional = Professional.objects.get(user=request.user)
            skill_id = request.data.get("id")

            if not skill_id:
                return Response({"detail": "Skill ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            skill = Skill.objects.get(id=skill_id)
            professional.skills.remove(skill)

            return Response(
                {"detail": "Skill removed successfully.", "skill": {"id": skill.id, "name": skill.name}},
                status=status.HTTP_200_OK
            )
        except Professional.DoesNotExist:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
        except Skill.DoesNotExist:
            return Response({"detail": "Skill not found."}, status=status.HTTP_404_NOT_FOUND)

class ProfessionalCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            professional = Professional.objects.get(user=request.user)
            category_names = request.data.get("names", [])  # Accept a list of category names

            if not category_names or not isinstance(category_names, list):
                return Response({"detail": "A list of category names is required."}, status=status.HTTP_400_BAD_REQUEST)

            added_categories = []
            for name in category_names:
                category, created = Category.objects.get_or_create(name=name)
                professional.categories.add(category)
                added_categories.append({"id": category.id, "name": category.name})

            return Response(
                {"detail": "Categories added successfully.", "categories": added_categories},
                status=status.HTTP_201_CREATED
            )
        except Professional.DoesNotExist:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            professional = Professional.objects.get(user=request.user)
            category_id = request.data.get("id")

            if not category_id:
                return Response({"detail": "Category ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            category = Category.objects.get(id=category_id)
            professional.categories.remove(category)

            return Response(
                {"detail": "Category removed successfully.", "category": {"id": category.id, "name": category.name}},
                status=status.HTTP_200_OK
            )
        except Professional.DoesNotExist:
            return Response({"detail": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)


class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        professional = request.user.professional
        serializer = CertificateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(professional=professional)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            certificate = Certificate.objects.get(id=pk, professional=request.user.professional)
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificateSerializer(certificate, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            certificate = Certificate.objects.get(id=pk, professional=request.user.professional)
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found."}, status=status.HTTP_404_NOT_FOUND)

        certificate.delete()
        return Response({"detail": "Certificate deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            professional = request.user.professional
            serializer = EducationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                print('serializer is valid')
                serializer.save(professional=professional)
                print('professional saved',serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            professional = request.user.professional
            education = Education.objects.get(pk=pk, professional=professional)
            serializer = EducationSerializer(education, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Education.DoesNotExist:
            return Response({"detail": "Education not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            # Get the professional and the education record to delete
            professional = request.user.professional
            education = Education.objects.get(pk=pk, professional=professional)
            education.delete()
            return Response({"detail": "Education deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Education.DoesNotExist:
            return Response({"detail": "Education not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            professional = request.user.professional
            serializer = PortfolioSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(professional=professional)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            professional = request.user.professional
            portfolio = Portfolio.objects.get(pk=pk, professional=professional)
            serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Portfolio.DoesNotExist:
            return Response({"detail": "Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            professional = request.user.professional
            portfolio = Portfolio.objects.get(pk=pk, professional=professional)
            portfolio.delete()
            return Response({"detail": "Portfolio deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Portfolio.DoesNotExist:
            return Response({"detail": "Portfolio not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalVerificationRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            professional = Professional.objects.get(user=user)
        except Professional.DoesNotExist:
            return Response({"error": "You must be a professional to request verification."}, status=status.HTTP_403_FORBIDDEN)
        
        if professional.is_verified:
            return Response({"error": "You are already verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        if VerificationRequest.objects.filter(professional=professional, status='pending').exists():
            return Response({"error": "A pending verification request already exists."}, status=status.HTTP_400_BAD_REQUEST)

        verification_request = VerificationRequest.objects.create(professional=professional)
        serializer = VerificationRequestSerializer(verification_request)

        return Response({"message": "Verification request submitted successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)


class ProfessionalSubscriptionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        professional = request.user.professional
        subscription_history = SubscriptionPlan.objects.filter(professional=professional)
        serializer = SubscriptionPlanSerializer(subscription_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




    
    
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        amount = data.get("amount")
        plan_type = data.get("plan_type")
        duration = data.get("duration")
        print('duration',duration)
        return_url = data.get("return_url")
        txt_ref = uuid.uuid4()
        
        if not plan_type or not duration:
            return Response(
                {"error": "Plan type and duration are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not amount:
            return Response(
                {"error": "Amount is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        professional = Professional.objects.filter(user=user, is_verified=True).first()
        if professional is None:
            return Response(
                {"error": "Professional not found or not verified."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Start a transaction block
        with transaction.atomic():
            active_subscription = SubscriptionPlan.objects.filter(
                professional=professional,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()

            payment = None
            if active_subscription:
                payment = Payment.objects.filter(
                    professional=professional,
                    subscription_plan=active_subscription
                ).first()

                if payment and payment.payment_status == 'completed':
                    return Response(
                        {
                            "error": "You are already subscribed to an active plan.",
                            "plan_type": active_subscription.plan_type,
                            "duration": active_subscription.duration,
                            "end_date": active_subscription.end_date.isoformat(),
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Check if the professional has enough balance
            if professional.balance < amount:
                return Response(
                    {"error": "Insufficient balance, please deposit enough amount."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Proceed with payment initiation
            chapa_url = "https://api.chapa.co/v1/transaction/initialize"
            chapa_api_key = settings.CHAPA_SECRET_KEY
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
                "Authorization": f"Bearer {chapa_api_key}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(chapa_url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    # Create a Payment record
                    if active_subscription:
                        payment = Payment.objects.filter(
                            professional=professional,
                            subscription_plan=active_subscription).first()
                        if payment is not None  and payment.payment_status !='completed':
                            print('payment is updated')
                            payment.subscription_plan = active_subscription
                            payment.amount = amount
                            payment.transaction_id = str(txt_ref)
                            payment.payment_status = 'pending'
                            payment.save()
                        else:
                            payment = Payment.objects.create(
                                subscription_plan=active_subscription,
                                professional=professional,
                                transaction_id=str(txt_ref),
                                amount=amount,
                                payment_status='pending')
                            payment.save()
                    else: 
                        subscription_plan = SubscriptionPlan(
                            professional=professional,
                            plan_type=plan_type,
                            duration=duration
                        )
                        subscription_plan.save()
                        payment = Payment.objects.create(
                            subscription_plan=subscription_plan,
                            professional=professional,
                            transaction_id=str(txt_ref),
                            amount=amount,
                            payment_status='pending'
                        )
                        payment.save()
                
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
                else:
                    error_message = response.json().get("message", "Failed to initiate payment.")
                    return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

            except requests.RequestException as e:
                return Response(
                    {"error": f"Payment request failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
class CheckPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Transaction not found."},
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
                
                payment.professional.balance -= payment.amount
                payment.professional.is_available=True
                payment.professional.save()
                
                payment_data = PaymentSerializer(payment).data
                
                return Response({
                        "message": "Payment status checked successfully.",
                        "data":{
                            "payment":payment_data},
                            "first_name":response_data.get("data", {}).get("first_name"),
                            "last_name":response_data.get("data", {}).get("last_name"),
                            "email":response_data.get("data", {}).get("email"),
                            "amount":response_data.get("data", {}).get("amount"),
                            "currency":response_data.get("data", {}).get("currency")
                         },status=status.HTTP_200_OK)
            else:
                payment.payment_status ='failed'
                payment.save()
                return Response(
                    {"error": "Failed to retrieve payment status from Chapa."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ServicePostSearchView(APIView):
    
    def get(self, request):
        
        query = request.GET.get('q', '')        
        
        results = []
        
         
        service_posts = ServicePost.objects.filter(
                Q(title__icontains=query) |             
                Q(description__icontains=query) |       
                Q(category__name__icontains=query)|
                Q(location__region__icontains=query)|
                Q(location__city__icontains=query),
                status='active',
                work_due_date__lte=timezone.now()
                    
            ).distinct() 

    
        serializer = ServicePostSerializer(service_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

