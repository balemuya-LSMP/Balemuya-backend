# from django.http import JsonResponse
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut

# def get_address_from_coordinates(latitude, longitude):
#     latitude = request.GET.get('latitude')
#     longitude = request.GET.get('longitude')

#     if not latitude or not longitude:
#         return JsonResponse({'error': 'Invalid input'}, status=400)

#     try:
#         latitude = float(latitude)
#         longitude = float(longitude)
#     except ValueError:
#         return JsonResponse({'error': 'Invalid latitude or longitude'}, status=400)

#     geolocator = Nominatim(user_agent="myGeocoder")

#     try:
#         location = geolocator.reverse((latitude, longitude),language='en')
#         if location:
#             # print('location address ', location.raw.get('address', {}))
#             # Split the address into components
#             address_components = location.raw.get('address', {})
#             print('address', address_components)
#             response_data = {
#                 'suburb': address_components.get('suburb', ''),
#                 'state_destrict': address_components.get('state_district', ''),
#                 'town': address_components.get('town', ''),
#                 'region': address_components.get('region', ''),
#                 'village': address_components.get('village', ''),
#                 'city': address_components.get('city', address_components.get('town', '')),
#                 'state': address_components.get('state', ''),
#                 'postal_code': address_components.get('postcode', ''),
#                 'country': address_components.get('country', ''),
#                 'country_code': address_components.get('country_code', ''),
#                 'iso_code': address_components.get('ISO3166-2-lvl4', '')
#             }
#             return JsonResponse(response_data)
#         else:
#             return JsonResponse({'error': 'Address not found'}, status=404)
#     except GeocoderTimedOut:
#         return JsonResponse({'error': 'Geocoding service timed out'}, status=500)