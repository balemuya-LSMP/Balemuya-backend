from django.urls import path
import uuid
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView,LoginView,VerifyEmailView,LogoutView,VerifyPhoneView,VerifyPasswordResetOTPView,ResendOTPView ,SetPasswordView,ResetPasswordView,\
UpdatePasswordView,GoogleLoginView,ProfileView,ProfileUpdateView,UserDetailView,UserDeleteView,UserBlockView ,\
    InitiatePaymentView, TrackPaymentView, PaymentCallbackView
urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
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
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('<uuid:id>/',UserDetailView.as_view(),name='user-detail'),
    path('<uuid:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('<uuid:pk>/block/',UserBlockView.as_view(),name='user-block'),
    # path("ws/initiate-payment/", consumers.PaymentInitiateConsumer.as_asgi()), 

    path('payment/initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/track/<str:transaction_id>/', TrackPaymentView.as_view(), name='track_payment'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),

]
