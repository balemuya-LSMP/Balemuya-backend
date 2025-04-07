from geopy.distance import geodesic
from users.models import Professional

def get_professionals_in_proximity_and_category(service_post, proximity_radius_km=300):
    if not service_post.location:
        raise ValueError("Service post must have a valid location with latitude and longitude.")

    job_location = (service_post.location.latitude, service_post.location.longitude)

    # Fetch professionals whose categories contain the service_post category
    professionals = Professional.objects.filter(categories__in=[service_post.category])

    professionals_in_proximity = []

    for professional in professionals:
        current_address = professional.user.address
        if not current_address:
            continue  # Skip professionals without an address

        professional_location = (current_address.latitude, current_address.longitude)
        
        try:
            distance = geodesic(job_location, professional_location).kilometers
            if distance <= proximity_radius_km:
                professionals_in_proximity.append(professional)
        except Exception as e:
            print(f"Error calculating distance for {professional}: {e}")

    return professionals_in_proximity
