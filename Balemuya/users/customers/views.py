from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from geopy.distance import geodesic
from users.models import User  # Assuming User model has user_type
from users.serializers import ProfessionalSerializer

class NearbyProfessionalsView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        customer_lat = request.user.address.latitude
        customer_lon = request.user.address.longitude
        customer_location = (customer_lat, customer_lon)

        nearby_professionals = self.find_nearby_professionals(customer_location,category,max_distance=10)
        if not nearby_professionals:
            return Response({"message": "No professionals found nearby"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "success", "nearby_professionals": nearby_professionals}, status=status.HTTP_200_OK)

    def find_nearby_professionals(self, customer_location, category=None, max_distance=None):
        nearby = []

        professionals = User.objects.filter(user_type='professional',is_available=True, professional__categories__name=category)

        for professional in professionals:
            if professional.address:
                professional_location = (professional.address.latitude, professional.address.longitude)
                distance = geodesic(customer_location, professional_location).kilometers
                
                # Check if the distance is within the specified max_distance
                if max_distance is None or distance <= max_distance:
                    nearby.append({
                        "id": professional.id,
                        "name": professional.first_name,
                        "user_type": professional.user_type,
                        "profile_image": professional.profile_image,
                        "address": professional.address.address,
                        "rating": professional.professional.rating,
                        "bio": professional.bio,
                        "distance": round(distance, 2)
                    })

        nearby.sort(key=lambda x: x['distance'])
        return nearby
    

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
        