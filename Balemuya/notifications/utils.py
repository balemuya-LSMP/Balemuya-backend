# utils.py

from geopy.distance import geodesic
from users.models import Professional  # Adjust the import based on your project structure

def get_professionals_in_proximity_and_category(service_post, proximity_radius_km=300):
    
    job_location = (service_post.location.latitude, service_post.location.longitude)
    professionals_in_proximity = []

    # Filter professionals by category
    professionals = Professional.objects.filter(categories__name__icontains=service_post.category)   
    print('professional in category is',professionals)

    for professional in professionals:
        # Get the professional's current address
        current_address = professional.user.address
        print('current address is',current_address)
        if current_address:
            professional_location = (current_address.latitude, current_address.longitude)
            
            # Calculate the distance
            distance = geodesic(job_location, professional_location).kilometers
            print('distance is',distance)
            # Check if within the proximity radius
            if distance <= proximity_radius_km:
                professionals_in_proximity.append(professional)

    return professionals_in_proximity