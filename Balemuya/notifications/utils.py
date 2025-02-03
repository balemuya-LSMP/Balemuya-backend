# utils.py

from geopy.distance import geodesic
from users.models import Professional  # Adjust the import based on your project structure

def get_professionals_in_proximity_and_category(service_post, proximity_radius_km=300):
    """
    Returns a list of professionals who are in the same category as the service post
    and within a specified proximity radius.

    :param service_post: The ServicePost instance containing job details.
    :param proximity_radius_km: The radius (in kilometers) to check for professionals.
    :return: List of professionals meeting the criteria.
    """
    job_location = (service_post.location.latitude, service_post.location.longitude)
    professionals_in_proximity = []

    # Filter professionals by category
    professionals = Professional.objects.filter(categories=service_post.category)
    print('professional in category is',professionals)

    for professional in professionals:
        # Get the professional's current address
        current_address = professional.user.addresses.filter(is_current=True).first()
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