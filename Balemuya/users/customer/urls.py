from django.urls import path
import uuid
from .views import CustomerProfileView,CustomerServicesView,NearbyProfessionalsView,FilterProfessionalsView,CustomerServiceRequestAPIView,CompleteServiceRequestAPIView,\
    CancelServiceRequestAPIView,UserSearchView,ServicePaymentTransferView,ServicePaymentVerifyView

urlpatterns = [
    path('<uuid:pk>/profile/',CustomerProfileView.as_view(), name='customer-profile'),
    path('nearby-professionals/',NearbyProfessionalsView.as_view(), name='nearby-professionals'),
    path('filter-professionals/',FilterProfessionalsView.as_view(), name='filter-professionals'),
    
    path('search-professional/',UserSearchView.as_view(),name='search-professional'),
    
    path('service-requests/', CustomerServiceRequestAPIView.as_view(), name='create-service-request'),  
    path('service-requests/<uuid:request_id>/cancel/', CancelServiceRequestAPIView.as_view(), name='cancel-service-request'),
    path('service-requests/<uuid:request_id>/complete/', CompleteServiceRequestAPIView.as_view(), name='Complete-service-request'),
      
    path('services/',CustomerServicesView.as_view(), name='customer-services'),
    
    path('services/payment/transfer/initiate/',ServicePaymentTransferView.as_view(), name='service-payment-transfer'),
    
    path('services/payment/transfer/verify/', ServicePaymentVerifyView.as_view(), name='service-payment-verify'),

    
    
]
