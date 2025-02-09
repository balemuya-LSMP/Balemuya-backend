from django.urls import path
from .views import ServicePostListCreateAPIView, ServicePostDetailAPIView,CreateServicePostApplicationAPIView, ListServicePostApplicationsAPIView,DetailServicePostApplicationAPIView,\
   AcceptServicePostApplicationAPIView, ServiceBookingRetrieveAPIView,ServiceBookingUpdateAPIView,ServiceBookingDeleteAPIView,ReviewBookingAPIView,ComplainBookingAPIView,CategoryListAPIView,\
       CancelServiceBookingAPIView

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    
    #service posts
    path('service-posts/', ServicePostListCreateAPIView.as_view(), name='service-post-list-create'),
    path('service-posts/<uuid:pk>/', ServicePostDetailAPIView.as_view(), name='service-post-detail'),
    
    path('service-posts/applications/create/', CreateServicePostApplicationAPIView.as_view(), name='create-service-post-application'),
    path('service-posts/customer/<uuid:service_id>/applications/', ListServicePostApplicationsAPIView.as_view(), name='list-service-post-applications'),
    path('service-posts/professional/applications/', ListServicePostApplicationsAPIView.as_view(), name='list-service-post-applications'),
    path('service-posts/applications/<uuid:pk>/', DetailServicePostApplicationAPIView.as_view(), name='detail-service-post-application'),
    path('service-posts/applications/<uuid:pk>/accept/', AcceptServicePostApplicationAPIView.as_view(), name='accept-service-post-application'),
   
   path('service-bookings/<uuid:pk>/', ServiceBookingRetrieveAPIView.as_view(), name='retrieve-service-booking'),
   path('service-bookings/<uuid:pk>/update/', ServiceBookingUpdateAPIView.as_view(), name='service-booking-update'),
   path('service-bookings/<uuid:pk>/delete/', ServiceBookingDeleteAPIView.as_view(), name='delete-service-booking'),
   path('service-bookings/<uuid:booking_id>/cancel/', CancelServiceBookingAPIView.as_view(), name='cancel-service-booking'),
    
    path('bookings/<uuid:booking_id>/review/', ReviewBookingAPIView.as_view(), name='review-booking'),
    path('bookings/<uuid:booking_id>/complain/create/', ComplainBookingAPIView.as_view(), name='complain'),
    
]
