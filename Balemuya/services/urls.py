from django.urls import path
from .views import ServicePostAPIView, ServicePostApplicationAPIView, ServiceBookingAPIView,ReviewBookingAPIView,ComplainBookingAPIView,CategoryListAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('service-posts/', ServicePostAPIView.as_view(), name='service-post-list-create'),
    path('service-posts/<uuid:pk>/', ServicePostAPIView.as_view(), name='service-post-detail'),
    path('service-posts/applications/', ServicePostApplicationAPIView.as_view(), name='service-post-application-create'),
    path('service-posts/<uuid:service_id>/applications/', ServicePostApplicationAPIView.as_view(), name='service-post-application-list'),
    path('service-posts/applications/<uuid:pk>/', ServicePostApplicationAPIView.as_view(), name='service-post-application-detail'),
    path('bookings/', ServiceBookingAPIView.as_view(), name='service-booking-create'),
    path('bookings/<uuid:pk>/', ServiceBookingAPIView.as_view(), name='service-booking-detail'),
    
    path('bookings/<uuid:booking_id>/review/', ReviewBookingAPIView.as_view(), name='review-booking'),
    path('bookings/<uuid:booking_id>/complain/', ComplainBookingAPIView.as_view(), name='complain'),
    
]
