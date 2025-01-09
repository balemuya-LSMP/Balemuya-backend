from django.urls import path
from .views import RegisterView
from allauth.account.views import ConfirmEmailView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='user-register'),
    path('auth/confirm-email/<str:key>/', ConfirmEmailView.as_view(), name='account_confirm_email'),  # Updated
]