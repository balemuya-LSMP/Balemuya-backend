# utils.py
from django.utils import timezone
from users.models import SubscriptionPlan, Professional

from geopy.distance import geodesic

def filter_service_posts_by_distance(service_posts, user_location, radius=500):
    filtered_posts = []
    
    user_latitude = user_location.latitude
    user_longitude = user_location.longitude
    print('here is called')
    for post in service_posts:
        post_location = (post.location.latitude, post.location.longitude)
        distance = geodesic((user_latitude, user_longitude), post_location).kilometers
        print('distance is',distance)
        print('posst is',post)
        if distance <= radius:
            post.distance = distance 
            filtered_posts.append(post)
    
    return filtered_posts


def check_professional_subscription(professional):
    current_time = timezone.now()
    active_subscription = SubscriptionPlan.objects.filter(
        professional=professional,
        end_date__lt=current_time
    ).first()
    print('i am called')

    if active_subscription and professional.is_available:
        professional.is_available = False
        professional.save()