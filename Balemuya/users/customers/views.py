from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic
from users.models import User  # Assuming User model has user_type
from users.serializers import ProfessionalSerializer

from .utils import find_nearby_professionals

class NearbyProfessionalsView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        customer_lat = request.user.address.latitude
        customer_lon = request.user.address.longitude
        customer_location = (customer_lat, customer_lon)

        nearby_professionals = find_nearby_professionals(customer_location,category,max_distance=10)
        if not nearby_professionals:
            return Response({"message": "No professionals found nearby"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "success", "nearby_professionals": nearby_professionals}, status=status.HTTP_200_OK)

    

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
        