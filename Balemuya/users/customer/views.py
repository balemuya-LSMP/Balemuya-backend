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

        nearby_professionals = find_nearby_professionals(customer_location,category)
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
        