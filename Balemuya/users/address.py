# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from .models import Address
from common.serializers import AddressSerializer

def get_address_components(latitude, longitude):
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.reverse((latitude, longitude), language='en')
        if location:
            return location.raw.get('address', {})
        return None
    except GeocoderTimedOut:
        return None

class AddressView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def post(self, request):
        existing_address = getattr(request.user, 'address', None)
        if existing_address:
            return Response({"error": "User already has an address."}, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        address_components = get_address_components(latitude, longitude) if latitude and longitude else None

        if address_components:
            city = address_components.get('city') or \
                    address_components.get('town') or \
                    address_components.get('village') or \
                    address_components.get('county') or \
                    address_components.get('suburb') or\
                    address_components.get('office') or\
                    address_components.get('road', '')

            region = address_components.get('region') or \
                     address_components.get('state') or \
                     address_components.get('state_district', '')

            country = address_components.get('country')

            request.data.update({
                'country': country,
                'region': region,
                'city': city,
                'latitude': latitude,
                'longitude': longitude
            })

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.user.address = serializer.save()
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            address = request.user.address
        except Address.DoesNotExist:
            return Response({"error": "Address not found to update"}, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude and longitude:
            address_components = get_address_components(latitude, longitude)
            if address_components:
                city = address_components.get('city') or \
                       address_components.get('town') or \
                       address_components.get('city_district') or \
                       address_components.get('village') or \
                       address_components.get('county') or \
                       address_components.get('suburb') or\
                       address_components.get('office') or\
                       address_components.get('road', '')


                region = address_components.get('region') or \
                         address_components.get('state') or \
                         address_components.get('state_district', '')

                country = address_components.get('country')

                request.data.update({
                    'country': country,
                    'region': region,
                    'city': city,
                    'latitude': latitude,
                    'longitude': longitude
                })

        serializer = self.serializer_class(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            address = request.user.address
            address.delete()
        except Address.DoesNotExist:
            return Response({"error": "Address not found to delete"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Address deleted successfully"}, status=status.HTTP_200_OK)