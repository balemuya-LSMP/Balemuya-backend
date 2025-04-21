from django.urls import path, include
import uuid
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterFCMDeviceView,RegisterView,LoginView,VerifyEmailView,LogoutView,VerifyPhoneView,VerifyPasswordResetOTPView,ResendOTPView ,SetPasswordView,ResetPasswordView,\
UpdatePasswordView,GoogleLoginView,ProfileView,UserUpdateView,UserDetailView,UserDeleteView,UserBlockView,UserFeedbackView,FavoriteListCreateAPIView
        
from .address import AddressView
urlpatterns = [
        # path('get-address/', get_address_from_coordinates, name='get_address'),

    
    path('register-device/', RegisterFCMDeviceView.as_view(), name='register_device'),

    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('auth/verify-phone/', VerifyPhoneView.as_view(), name='account_phone_verification_sent'),
    path('auth/login/',LoginView.as_view(), name='user-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/',LogoutView.as_view(), name='user-logout'),
    path('auth/verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/verify-pass-reset-otp/', VerifyPasswordResetOTPView.as_view(), name='verify-pas-res-otp'),
    path('auth/set-new-password/', SetPasswordView.as_view(), name='set-password'),
    path('auth/update-password/', UpdatePasswordView.as_view(), name='update-password'),
    
    path('auth/google-signin/',GoogleLoginView.as_view(), name='google-login'),
    
    path('profile/',ProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='user-update'),
    path('profile/address/',AddressView.as_view(), name='address-create-update-delete'),
    path('<uuid:id>/',UserDetailView.as_view(),name='user-detail'),
    path('<uuid:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('<uuid:pk>/block/',UserBlockView.as_view(),name='user-block'),
    
    path('professional/',include('users.professional.urls')),
    path('customer/',include('users.customer.urls')),
    
    #feedback
    path('feedback/add/', UserFeedbackView.as_view(), name='user-feedback'),
    path('feedbacks/', UserFeedbackView.as_view(), name='user-feedback'),
    
    path('favorites/', FavoriteListCreateAPIView.as_view(), name='favorite_list_create'),  

    
    
   
]
