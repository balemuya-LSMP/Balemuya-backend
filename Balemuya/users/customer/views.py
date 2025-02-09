from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic
from users.models import User  # Assuming User model has user_type
from users.serializers import ProfessionalSerializer,CustomerSerializer
from services.models import ServicePost, Review, ServicePostApplication, ServiceBooking
from services.serializers import ServicePostSerializer, ReviewSerializer, ServicePostApplicationSerializer, ServiceBookingSerializer

from .utils import find_nearby_professionals

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
            user = User.objects.get(id=pk, user_type='customer')
        except User.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
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
        else:
            return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)


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
                service_canceled = ServiceBooking.objects.filter(application__srvice__customer=request.user.customer,status='canceled').order_by('-created_at')
                service_canceled_serializer = ServiceBookingSerializer(service_canceled, many=True)
                return Response({"data": list(service_canceled_serializer.data)}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid status parameter."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
           





class FilterProfessionalsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        category = request.query_params.get('category')
        distance = request.query_params.get('distance')
        rating = request.query_params.get('rating')
        
        professionals = self.filter_professionals(category, distance, rating)
        
        return Response({"message": "success", "professionals": professionals}, status=status.HTTP_200_OK)
        
    def filter_professionals(self, category, distance, rating):
        professionals = User.objects.filter(user_type='professional', professional__categories__name=category)
        
        if distance:
            professionals = professionals.filter(address__distance_lte=(distance, 'km'))
        
        if rating:
            professionals = professionals.filter(professional__rating__gte=rating)
        
        return ProfessionalSerializer(professionals, many=True).data
        