from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from geopy.distance import geodesic
from users.models import User  # Assuming User model has user_type
from users.serializers import ProfessionalSerializer

class NearbyProfessionalsView(APIView):
    def get(self, request):
        # Get the customer's location from the user's address
        customer_lat = request.user.address.latitude
        customer_lon = request.user.address.longitude
        customer_location = (customer_lat, customer_lon)

        nearby_professionals = self.find_nearby_professionals(customer_location)

        return Response({"message": "success", "nearby_professionals": nearby_professionals}, status=status.HTTP_200_OK)

    def find_nearby_professionals(self, customer_location):
        nearby = []

        professionals = User.objects.filter(user_type='professional')

        for professional in professionals:
            # Ensure the professional has an address
            if professional.address:
                professional_location = (professional.address.latitude, professional.address.longitude)
                distance = geodesic(customer_location, professional_location).kilometers
                nearby.append({
                    "id": professional.id,
                    "name": professional.first_name,
                    "user_type": professional.user_type,
                    "latitude": professional.address.latitude,
                    "longitude": professional.address.longitude,
                    "distance": round(distance, 2)
                })

        nearby.sort(key=lambda x: x['distance'])
        return nearby
