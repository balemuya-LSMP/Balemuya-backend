from django.urls import path
import uuid
from .views import ProfessionalListView,CustomerListView,AdminListView

from .views import (
    ProfessionalListView,
    AdminVerifyProfessionalView,
    CustomerListView,
    AdminListView,
    ProfessionalVerificationRequestListView,
    StatisticsView    ,
    AdminServicePostReportListView,
    AdminDeleteReportedPostView
)

urlpatterns = [
    # List all professionals
    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<uuid:pk>/verify/', AdminVerifyProfessionalView.as_view(), name='verify-professional'),
    path('professional/verification/requests/', ProfessionalVerificationRequestListView.as_view(), name='professional-verification-request'),
    
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    # path('services/', ServiceListView.as_view(), name='service-list'),
    # path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/reported-posts/', AdminServicePostReportListView.as_view(), name='servicepost-report-list'),
    path('services/<uuid:service_post_id>/delete/', AdminDeleteReportedPostView.as_view(), name='admin-delete-reported-post'),
    
    path('admins/', AdminListView.as_view(), name='admin-list'),

    path('stats/', StatisticsView.as_view(), name='user-stats'),
    
    
]
