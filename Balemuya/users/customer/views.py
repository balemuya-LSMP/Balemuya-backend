from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic
from common.serializers import UserSerializer
from users.models import User, Customer,Professional
from users.serializers import ProfessionalSerializer,CustomerSerializer
from services.models import ServicePost, Review, ServicePostApplication, ServiceBooking,ServiceRequest
from services.serializers import ServicePostSerializer, ReviewSerializer, ServicePostApplicationSerializer, ServiceBookingSerializer,ServiceRequestSerializer

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
            return Response({'error': f'Customer not found '}, status=status.HTTP_404_NOT_FOUND)
        customer = user.customer
        active_service_posts = ServicePost.objects.filter(customer=user.customer,status='active').order_by('-created_at')
        booked_service_posts = ServicePost.objects.filter(customer=user.customer,status='booked').order_by('-created_at')
        completed_service_posts = ServicePost.objects.filter(customer=user.customer,status='completed').order_by('-created_at')
            
        customer_serializer = CustomerSerializer(customer)
        active_service_posts_serializer = ServicePostSerializer(active_service_posts, many=True)
        booked_service_posts_serializer = ServicePostSerializer(booked_service_posts, many=True)
        completed_service_posts_serializer = ServicePostSerializer(completed_service_posts, many=True)
        reviews = Review.objects.filter(booking__application__service__customer=user.customer).order_by('-created_at')
            
        response_data = {
                'customer': customer_serializer.data,
                'active_service_posts': active_service_posts_serializer.data,
                'booked_service_posts': booked_service_posts_serializer.data,
                'completed_service_posts': completed_service_posts_serializer.data,
                'reviews': ReviewSerializer(reviews, many=True).data
            }
            
        return Response({'data': response_data}, status=status.HTTP_200_OK)
        


class CustomerServicesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type == "customer":
            query_param_status = request.query_params.get('status', None)
            if query_param_status is None:
                new_service_post = ServicePost.objects.filter(customer=request.user.customer,status='active').order_by('-created_at')
                new_service_post_serializer = ServicePostSerializer(new_service_post, many=True)
                return Response({"data": list(new_service_post_serializer.data)}, status=status.HTTP_200_OK)
           
            elif query_param_status == 'booked':
                service_booked = ServiceBooking.objects.filter(application__service__customer=request.user.customer,status='pending').order_by('-created_at')
                service_booked_serializer = ServiceBookingSerializer(service_booked, many=True)
                
                return Response({"data": list(service_booked_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'completed':
                service_completed = ServiceBooking.objects.filter(application__service__customer=request.user.customer,status='completed').order_by('-created_at')
                service_completed_serializer = ServiceBookingSerializer(service_completed, many=True)
                return Response({"data": list(service_completed_serializer.data)}, status=status.HTTP_200_OK)
            elif query_param_status == 'canceled':
                service_canceled = ServicePost.objects.filter(customer=request.user.customer,status='canceled').order_by('-created_at')
                service_canceled_serializer = ServicePostSerializer(service_canceled, many=True)
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

        if distance is not None:
            try:
                distance = float(distance)
            except ValueError:
                return Response({"error": "Invalid distance value."}, status=status.HTTP_400_BAD_REQUEST)

        if rating is not None:
            try:
                rating = float(rating)
            except ValueError:
                return Response({"error": "Invalid rating value."}, status=status.HTTP_400_BAD_REQUEST)
        user_location = None
        if request.user.address:
            user_location = (request.user.address.latitude,request.user.address.longitude)
        professionals = filter_professionals(current_location=user_location, categories=categories, rating=rating, max_distance=distance)

        return Response({"message": "success", "professionals": professionals}, status=status.HTTP_200_OK)
    
class CustomerServiceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        status_param = request.query_params.get('status')

        service_requests = ServiceRequest.objects.filter(customer=user.customer,status='pending')

        if status_param:
            service_requests = service_requests.filter(status=status_param)

        serializer = ServiceRequestSerializer(service_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = {
            'customer': user.customer.id,
            'professional': request.data.get('professional'),
            'detail': request.data.get('detail'),
        }

        serializer = ServiceRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Service request sent."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelServiceRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')

        try:
            service_request = ServiceRequest.objects.get(id=request_id, customer=request.user.customer)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found or you are not authorized."}, status=status.HTTP_404_NOT_FOUND)

        service_request.status = 'canceled'
        service_request.save()

        return Response({"success": "Service request canceled."}, status=status.HTTP_200_OK)
    
    
    
class UserSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')

        professionals = Professional.objects.filter(
            Q(categories__name__icontains=query) | 
            Q(skills__name__icontains=query) |      
            Q(user__first_name__icontains=query) |            
            Q(user__address__city__icontains=query) |             
            Q(user__address__region__icontains=query),               
            is_verified=True,
            is_available=True,
        ).select_related('user').order_by('-rating').distinct()  # Order by rating descending
        
        paginator = CustomPagination()
        paginated_results = paginator.paginate_queryset(professionals, request)

        serializer = UserSerializer([professional.user for professional in paginated_results], many=True)
        
        return paginator.get_paginated_response(serializer.data)