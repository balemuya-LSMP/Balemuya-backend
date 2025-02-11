from django.urls import path
import uuid
from .views import CustomerProfileView,CustomerServicesView,NearbyProfessionalsView,FilterProfessionalsView,CustomerServiceRequestAPIView,CancelServiceRequestAPIView

urlpatterns = [
    path('<uuid:pk>/profile/',CustomerProfileView.as_view(), name='customer-profile'),
    path('nearby-professionals/',NearbyProfessionalsView.as_view(), name='nearby-professionals'),
    path('filter-professionals/',FilterProfessionalsView.as_view(), name='filter-professionals'),
    
    path('service-request/', CustomerServiceRequestAPIView.as_view(), name='create_service_request'),  
    path('service-request/<int:request_id>/cancel/', CancelServiceRequestAPIView.as_view(), name='cancel_service_request'),
      
    path('services/',CustomerServicesView.as_view(), name='customer-services'),
]
