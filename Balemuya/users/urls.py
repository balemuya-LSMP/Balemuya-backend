from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView,LoginView,VerifyEmailView,LogoutView,VerifyPhoneView,VerifyPaswordResetOTPView,ResendOTPView,SetPasswordView,ResetPasswordView,UpdatePasswordView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('auth/login/',LoginView.as_view(), name='user-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/',LogoutView.as_view(), name='user-logout'),
    path('auth/verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/verify-pass-reset-otp/', VerifyPaswordResetOTPView.as_view(), name='verify-otp'),
    path('auth/set-password/', SetPasswordView.as_view(), name='set-password'),
    path('auth/update-password/', UpdatePasswordView.as_view(), name='update-password'),
      
]