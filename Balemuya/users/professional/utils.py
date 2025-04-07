# utils.py
from geopy.distance import geodesic

def filter_service_posts_by_distance(service_posts, user_location, radius=50):
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