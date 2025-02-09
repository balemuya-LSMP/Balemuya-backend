from django.urls import path
import uuid
from .views import CustomerProfileView,NearbyProfessionalsView

urlpatterns = [
    path('<uuid:pk>/profile/',CustomerProfileView.as_view(), name='customer-profile'),
    path('nearby-professionals/',NearbyProfessionalsView.as_view(), name='nearby-professionals'),
]
