from django.urls import path
import uuid
from .views import CustomerProfileView,CustomerServicesView,NearbyProfessionalsView

urlpatterns = [
    path('<uuid:pk>/profile/',CustomerProfileView.as_view(), name='customer-profile'),
    path('nearby-professionals/',NearbyProfessionalsView.as_view(), name='nearby-professionals'),
    
    path('services/',CustomerServicesView.as_view(), name='customer-services'),
]
