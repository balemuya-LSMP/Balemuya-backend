from django.urls import path
import uuid
from .views import ProfessionalListView,CustomerListView,AdminListView

from .views import (
    ProfessionalListView,
    AdminVerifyProfessionalView,
    CustomerListView,
    AdminListView,
    ProfessionalVerificationRequestListView,
    # CustomerStatisticsView
    
)

urlpatterns = [
    # List all professionals
    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<uuid:pk>/verify/', AdminVerifyProfessionalView.as_view(), name='verify-professional'),
    path('professional/verification/requests/', ProfessionalVerificationRequestListView.as_view(), name='professional-verification-request'),
   
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    # path('customers/statistics/', CustomerStatisticsView.as_view(), name='customer-statistics'),
    
    path('admins/', AdminListView.as_view(), name='admin-list'),
]
