from django.urls import path
from .views import RegisterView
from allauth.account.views import ConfirmEmailView
from .utils import send_sms

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/call/', send_sms, name='send-sms'),
    path('auth/confirm-email/<str:key>/', ConfirmEmailView.as_view(), name='account_confirm_email'),  # Updated
]