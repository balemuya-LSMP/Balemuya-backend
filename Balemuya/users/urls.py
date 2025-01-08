from django.urls import path
from .views import RegisterView

from allauth.account.views import ConfirmEmailView
# In your urls.py
urlpatterns = [
 path('auth/register/', RegisterView.as_view(), name='user-register'),
 path('auth/confirm-email', ConfirmEmailView.as_view(), name='account_confirm_email'),

]

