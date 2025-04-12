from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from geopy.distance import geodesic
from users.models import User  
from users.serializers import ProfessionalSerializer
from common.serializers import AddressSerializer


def find_nearby_professionals(customer_location, max_distance=50,rating=None,category=None,):
        nearby = []

        professionals = Professional.objects.filter(user__user_type='professional',user__is_active=True,user__is_blocked=False,is_verified=True,is_available=True)

        for professional in professionals:
            if professional.address:
                professional_location = (professional.address.latitude, professional.address.longitude)
                distance = geodesic(customer_location, professional_location).kilometers
                
                if max_distance is None or distance <= max_distance:
                    nearby.append({
                        "id": professional.user.id,
                        "name": professional.user.username,
                        "user_type": professional.user.user_type,
                        "profile_image": professional.user.profile_image.url,
                        "address": AddressSerializer(professional.user.address).data,
                        "rating": professional.rating,
                        "bio": professional.user.bio,
                        "distance": round(distance, 2)
                    })

        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
    
def filter_professionals(current_location=None, categories=None,entity_type=None, rating=None, max_distance=50):
    filtered = []

    professionals = Professional.objects.filter(user__user_type='professional',user__is_active=True,user__is_blocked=False,is_verified=True, is_available=True)

    if entity_type:
        professionals = professionals.filter(user__entity_type=entity_type)
    if categories:
        professionals = professionals.filter(categories__name__in=categories).distinct()

    if rating:
        professionals = professionals.filter(rating__gte=rating)

    if current_location:
        for professional in professionals:
            if professional.user.address:
                professional_location = (professional.user.address.latitude, professional.user.address.longitude)
                distance = geodesic(current_location, professional_location).kilometers

                # Check if the distance is within the max_distance
                if max_distance is None or distance <= max_distance:
                    filtered.append({
                        "id": professional.user.id,
                        "name": professional.user.username,
                        "user_type": professional.user.user_type,
                        "profile_image": professional.user.profile_image.url,
                        "address": AddressSerializer(professional.user.address).data,
                        "rating": professional.rating,
                        "bio": professional.user.bio,
                        "distance": round(distance, 2)
                    })

        filtered.sort(key=lambda x: x['distance'])
    else:
        filtered = [
            {
                "id": professional.user.id,
                "name": professional.user.username,
                "user_type": professional.user.user_type,
                "profile_image": professional.user.profile_image.url,
                "address": AddressSerializer(professional.user.address).data,
                "rating": professional.rating,
                "bio": professional.user.bio,
            }
            for professional in professionals
            if professional.address is not None
        ]

    return filtered

            
            
        

    