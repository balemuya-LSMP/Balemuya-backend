from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.db import transaction
import requests
import uuid
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic
from common.serializers import UserSerializer
from users.models import User, Customer,Professional,Payment,BankAccount
from users.serializers import ProfessionalSerializer,CustomerSerializer,PaymentSerializer,BankAccountSerializer
from services.models import ServicePost, Review, ServicePostApplication, ServiceBooking,ServiceRequest
from services.serializers import ServicePostSerializer,ServicePostDetailSerializer, ReviewSerializer,ReviewDetailSerializer, ServicePostApplicationSerializer,ServicePostApplicationDetailSerializer, ServiceBookingSerializer,ServiceBookingDetailSerializer,\
    ServiceRequestSerializer,ServiceRequestDetailSerializer

from .utils import find_nearby_professionals,filter_professionals
from users.pagination import CustomPagination

class NearbyProfessionalsView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        customer_lat = request.user.address.latitude
        customer_lon = request.user.address.longitude
        customer_location = (customer_lat, customer_lon)

        nearby_professionals = find_nearby_professionals(customer_location,max_distance=50)
        if not nearby_professionals:
            return Response({"message": "No professionals found nearby"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "success", "nearby_professionals": nearby_professionals}, status=status.HTTP_200_OK)

    
    
class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk):
        try:
            user = User.objects.get(id=pk,user_type='customer')
        except User.DoesNotExist as e:
            return Response({'detail': f'Customer not found '}, status=status.HTTP_404_NOT_FOUND)
        customer = user.customer
        active_service_posts = ServicePost.objects.filter(customer=user.customer,status='active').order_by('-created_at')
        booked_service_posts = ServicePost.objects.filter(customer=user.customer,status='booked').order_by('-created_at')
        completed_service_posts = ServicePost.objects.filter(customer=user.customer,status='completed').order_by('-created_at')
            
        customer_serializer = CustomerSerializer(customer)
        active_service_posts_serializer = ServicePostDetailSerializer(active_service_posts, many=True)
        booked_service_posts_serializer = ServicePostDetailSerializer(booked_service_posts, many=True)
        completed_service_posts_serializer = ServicePostDetailSerializer(completed_service_posts, many=True)
        reviews = Review.objects.filter(booking__application__service__customer=user.customer).order_by('-created_at')
            
        response_data = {
                'customer': customer_serializer.data,
                'active_service_posts': active_service_posts_serializer.data,
                'booked_service_posts': booked_service_posts_serializer.data,
                'completed_service_posts': completed_service_posts_serializer.data,
                'reviews': ReviewDetailSerializer(reviews, many=True).data
            }
            
        return Response({'data': response_data}, status=status.HTTP_200_OK)
        


class CustomerServicesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type == "customer":
            query_param_status = request.query_params.get('status', None)
            if query_param_status is None:
                new_service_post = ServicePost.objects.filter(customer=request.user.customer,status='active').order_by('-created_at')
                new_service_post_serializer = ServicePostDetailSerializer(new_service_post, many=True)
                return Response({"data": list(new_service_post_serializer.data)}, status=status.HTTP_200_OK)
           
            elif query_param_status == 'booked':
                service_booked = ServiceBooking.objects.filter(application__service__customer=request.user.customer,status='pending').order_by('-created_at')
                service_booked_serializer = ServiceBookingDetailSerializer(service_booked, many=True)
                
                return Response({"data": list(service_booked_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'completed':
                service_completed = ServiceBooking.objects.filter(application__service__customer=request.user.customer,status='completed').order_by('-created_at')
                service_completed_serializer = ServiceBookingDetailSerializer(service_completed, many=True)
                return Response({"data": list(service_completed_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'canceled':
                service_canceled = ServicePost.objects.filter(customer=request.user.customer,status='canceled').order_by('-created_at')
                service_canceled_serializer = ServicePostDetailSerializer(service_canceled, many=True)
                return Response({"data": list(service_canceled_serializer.data)}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid status parameter."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
           

class FilterProfessionalsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = request.query_params.getlist('categories')
        distance = request.query_params.get('distance')
        rating = request.query_params.get('rating')
        entity_type = request.query_params.get('entity_type')

        if distance is not None:
            try:
                distance = float(distance)
            except ValueError:
                return Response({"detail": "Invalid distance value."}, status=status.HTTP_400_BAD_REQUEST)

        if rating is not None:
            try:
                rating = float(rating)
            except ValueError:
                return Response({"detail": "Invalid rating value."}, status=status.HTTP_400_BAD_REQUEST)
        user_location = None
        if request.user.address:
            user_location = (request.user.address.latitude,request.user.address.longitude)
        professionals = filter_professionals(current_location=user_location, categories=categories, rating=rating,entity_type=entity_type, max_distance=distance)

        return Response({"message": "success", "professionals": professionals}, status=status.HTTP_200_OK)
    
class CustomerServiceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        status_param = request.query_params.get('status')

        service_requests = ServiceRequest.objects.filter(customer=user.customer).order_by('-updated_at')

        if status_param:
            service_requests = service_requests.filter(status=status_param)
        else:
            service_requests = service_requests.filter(status='pending')
        serializer = ServiceRequestDetailSerializer(service_requests, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
       
    

    def post(self, request, *args, **kwargs):
            customer_user = request.user.customer
            professional_user_id = request.data.get('professional')

            try:
                professional_user =User.objects.get(id=professional_user_id)
            except Professional.DoesNotExist:
                return Response({"detail": "Professional does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'customer': customer_user.id,  
                'professional': professional_user.professional.id, 
                'detail': request.data.get('detail'),
            }

            serializer = ServiceRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Service request sent."}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class CancelServiceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')

        try:
            service_request = ServiceRequest.objects.get(id=request_id, customer=request.user.customer)
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        service_request.status = 'canceled'
        service_request.save()

        return Response({"message": "Service request canceled."}, status=status.HTTP_200_OK)
    
class CompleteServiceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        if not request.user.user_type =='customer':
            return Response({"detail": "user is not customer."},status=status.HTTP_401_UNAUTHORIZED)

            

        try:
            service_request = ServiceRequest.objects.get(id=request_id, customer=request.user.customer,status='accepted')
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        service_request.status = 'completed'
        service_request.save()

        return Response({"message": "Service request completed."}, status=status.HTTP_200_OK)
    
    
    
class UserSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')

        professionals = Professional.objects.filter(
            Q(categories__name__icontains=query) | 
            Q(skills__name__icontains=query) |      
            Q(user__username__icontains=query) |            
            Q(user__address__city__icontains=query) |             
            Q(user__address__region__icontains=query),
            user__is_blocked=False,
            user__is_active=True,               
            is_verified=True,
            is_available=True,
        ).select_related('user').order_by('-rating').distinct() 
        
        paginator = CustomPagination()
        paginated_results = paginator.paginate_queryset(professionals, request)

        serializer = UserSerializer([professional.user for professional in paginated_results], many=True)
        
        return paginator.get_paginated_response(serializer.data)

class ServicePaymentTransferView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated via JWT

    def post(self, request):
        # Check if the user is a customer
        if request.user.user_type != 'customer':
            return Response({'detail': 'User is not a customer.'}, status=status.HTTP_401_UNAUTHORIZED)

        customer = request.user.customer
        payment_type = request.data.get('payment_type')
        professional_id = request.data.get('professional')
        amount = request.data.get('amount')
        booking_id = request.data.get('booking')
        request_id = request.data.get('service_request')
        return_url = request.data.get('return_url')

        if not professional_id or not amount or not payment_type:
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate professional UUID
        try:
            professional_uuid = uuid.UUID(professional_id)
        except ValueError:
            return Response({'detail': 'Invalid UUID format for professional.'}, status=status.HTTP_400_BAD_REQUEST)

        booking = None
        service_request = None

        if payment_type == 'job_post':
            # Validate booking UUID
            try:
                booking_uuid = uuid.UUID(booking_id)
                booking = ServiceBooking.objects.get(
                    id=booking_uuid,
                    application__service__customer=customer,
                    application__professional=professional_uuid
                )
            except (ValueError, ServiceBooking.DoesNotExist):
                return Response({'detail': 'Booking not found or invalid UUID.'}, status=status.HTTP_404_NOT_FOUND)

        elif payment_type == 'direct_request':
            # Validate service request UUID
            
            service_request_uuid = uuid.UUID(request_id)
            print('professional',Professional.objects.get(id=professional_uuid))
            serv_req = ServiceRequest.objects.get(id=service_request_uuid)
            print('customer is,',serv_req.customer)
            try:
                service_request = ServiceRequest.objects.get(
                    id=service_request_uuid,
                    customer=customer,
                    professional=professional_uuid,
                    status='completed',
                )
            except (ValueError, ServiceRequest.DoesNotExist):
                return Response({'detail': 'Request not found or invalid UUID.'}, status=status.HTTP_404_NOT_FOUND)

        # Validate professional existence
        try:
            professional = Professional.objects.select_related('bank_account').get(id=professional_uuid)
        except Professional.DoesNotExist:
            return Response({'detail': 'Professional does not have a bank account.'}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(professional, 'bank_account'):
            return Response({'detail': 'Professional has no bank account configured.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction_reference = str(uuid.uuid4())
        payment_url = "https://api.chapa.co/v1/transaction/initialize"

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": request.user.email,
            "first_name": customer.user.first_name,
            "last_name": customer.user.last_name,
            "phone_number": customer.user.phone_number,
            "tx_ref": transaction_reference,
            "description": f"Payment for service by {professional.user.username}",
            "return_url": f'{return_url}?transaction_id={transaction_reference}',
        }

        headers = {
            'Authorization': f"Bearer {settings.CHAPA_SECRET_KEY}",
            'Content-Type': 'application/json'
        }

        # Process payment
        try:
            response = requests.post(payment_url, json=payload, headers=headers)
            response.raise_for_status()
            res_data = response.json()

            if res_data.get("status") == "success":
                payment_data = {
                    "customer": customer,
                    "professional": professional,
                    "amount": amount,
                    "payment_type": payment_type,
                    "payment_status": 'pending',
                    "transaction_id": transaction_reference
                }
                
                if payment_type == 'job_post':
                    payment_data["booking"] = booking
                elif payment_type == 'direct_request':
                    payment_data["service_request"] = service_request

                Payment.objects.create(**payment_data)

                return Response({
                    "data": {
                        "payment_url": res_data.get("data", {}).get("checkout_url"),
                        "transaction_id": transaction_reference
                    }
                }, status=status.HTTP_200_OK)

            return Response({
                "message": f"Failed to create payment session: {res_data.get('message')}",
                "status": "failed"
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({
                "message": f"Error connecting to Chapa: {str(e)}",
                "status": "failed"
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
class ServicePaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]
  
    def post(self, request):

        tx_ref = request.data.get('tx_ref')
        
        if not tx_ref:
            return Response({
                'detail': 'Transaction reference (tx_ref) is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({
                'detail': 'Payment not found with the given transaction reference.'
            }, status=status.HTTP_404_NOT_FOUND)

        verify_url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'

        headers = {
            'Authorization': f"Bearer {settings.CHAPA_SECRET_KEY}",
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(verify_url, headers=headers)
            response.raise_for_status()
            res_data = response.json()
            
            payment = Payment.objects.filter(transaction_id=tx_ref,customer=request.user.customer).first()
            if payment.payment_status =='completed':
                return Response({'detail':"payment already verified"},status = status.HTTP_400_BAD_REQUEST)
            if res_data.get('status') == 'success':
                payment.payment_status = 'completed'
                payment.save()

                professional = payment.professional
                professional.balance += payment.amount 
                professional.save()
                
                print('professional balance',professional.balance)

                return Response({
                    'detail': f'Payment verified successfully and professional balance updated. balance {professional.balance}'
                }, status=status.HTTP_200_OK)
            else:
                payment.payment_status = 'failed'
                payment.save()

                return Response({
                    'detail': 'Payment verification failed.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.RequestException as e:
            return Response({
                'message': f"Error verifying payment with Chapa: {str(e)}",
                'status': 'failed'
            }, status=status.HTTP_400_BAD_REQUEST)

