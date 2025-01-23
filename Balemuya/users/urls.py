from django.urls import path
import uuid
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterFCMDeviceView,RegisterView,LoginView,VerifyEmailView,LogoutView,VerifyPhoneView,VerifyPasswordResetOTPView,ResendOTPView ,SetPasswordView,ResetPasswordView,\
UpdatePasswordView,GoogleLoginView,ProfileView,UserUpdateView,UserDetailView,UserDeleteView,UserBlockView ,\
    ProfessionalVerificationRequestView,InitiatePaymentView, TrackPaymentView, PaymentCallbackView,MarkNotificationAsReadView,NotificationListView,\
        CertificateView, EducationView, PortfolioView, ProfessionalSkillView, ProfessionalCategoryView,AddressView
urlpatterns = [
    
    path('register-device/', RegisterFCMDeviceView.as_view(), name='register_device'),

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
    path('profile/update/', UserUpdateView.as_view(), name='user-update'),
    path('profile/address/create/',AddressView.as_view(), name='address-create'),
    path('profile/address/<uuid:pk>/',AddressView.as_view(), name='address-update-delete'),
    path('<uuid:id>/',UserDetailView.as_view(),name='user-detail'),
    path('<uuid:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('<uuid:pk>/block/',UserBlockView.as_view(),name='user-block'),
    
    path('professional/profile/skills/', ProfessionalSkillView.as_view(), name='skill-create-update-delete'),
    path('professional/profile/categories/', ProfessionalCategoryView.as_view(), name='category-create-delete'),
    
    path('professional/profile/certificates/add/', CertificateView.as_view(), name='certificate-create'),  # POST
    path('professional/profile/certificates/<uuid:pk>/update/', CertificateView.as_view(), name='certificate-update'),  # PUT
    path('professional/profile/certificates/<uuid:pk>/delete/', CertificateView.as_view(), name='certificate-delete'),  # DELETE
    
    path('professional/profile/educations/add/', EducationView.as_view(), name='education-create'),  # POST
    path('professional/profile/educations/<uuid:pk>/update/', EducationView.as_view(), name='education-update'),  # PUT
    path('professional/profile/educations/<uuid:pk>/delete/', EducationView.as_view(), name='education-delete'),  # DELETE
    
    path('professional/profile/portfolios/add/', PortfolioView.as_view(), name='portfolio-create'),  # POST
    path('professional/profile/portfolios/<uuid:pk>/update/', PortfolioView.as_view(), name='portfolio-update'),  # PUT
    path('professional/profile/portfolios/<uuid:pk>/delete/', PortfolioView.as_view(), name='portfolio-delete'),  # DELETE
    path('professional/verification-requests/', ProfessionalVerificationRequestView.as_view(), name='professional-verification-request'),

    # path("ws/initiate-payment/", consumers.PaymentInitiateConsumer.as_asgi()), 

    #payment related
    path('payment/initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/track/<str:transaction_id>/', TrackPaymentView.as_view(), name='track_payment'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    
    #Notification related views
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),

]
