from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from geopy.distance import geodesic
from users.models import User  # Assuming User model has user_type
from users.serializers import ProfessionalSerializer
from common.serializers import AddressSerializer


def find_nearby_professionals(self, customer_location, category=None, max_distance=None):
        nearby = []

        professionals = User.objects.filter(user_type='professional',professional__is_available=True, professional__categories__name=category)

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
                        "profile_image": professional.profile_image.url,
                        "address": AddressSerializer(professional.address).data,
                        "rating": professional.professional.rating,
                        "bio": professional.bio,
                        "distance": round(distance, 2)
                    })

        nearby.sort(key=lambda x: x['distance'])
        return nearby
