from django.urls import path
from .views import ServicePostAPIView, ServicePostApplicationAPIView, ServiceBookingAPIView,ReviewBookingAPIView,ComplainBookingAPIView

urlpatterns = [
    path('service-posts/', ServicePostAPIView.as_view(), name='service-post-list-create'),
    path('service-posts/<uuid:pk>/', ServicePostAPIView.as_view(), name='service-post-detail'),
    path('service-posts/<uuid:service_post_id>/applications/', ServicePostApplicationAPIView.as_view(), name='service-post-application-list-create'),
    path('applications/<uuid:pk>/', ServicePostApplicationAPIView.as_view(), name='service-post-application-detail'),
    path('bookings/', ServiceBookingAPIView.as_view(), name='service-booking-create'),
    path('bookings/<uuid:pk>/', ServiceBookingAPIView.as_view(), name='service-booking-detail'),
    
    path('bookings/<uuid:pk>/review/', ReviewBookingAPIView.as_view(), name='review-booking'),
    path('bookings/<uuid:pk>/complain/', ComplainBookingAPIView.as_view(), name='complain'),
    
]
