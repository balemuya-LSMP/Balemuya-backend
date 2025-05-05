from django.urls import path
import uuid
from .views import ProfessionalListView,CustomerListView,AdminListView

from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    UserListView,
    UserCreateView,
    UserDetailView,
    UserBlockView,
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
    
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list'), #manage categories
    path('categories/<uuid:category_id>/', CategoryDetailView.as_view(), name='category-update'),
    
    #user related 
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/create/', UserListView.as_view(), name='user-list'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-update'),
    path('users/<uuid:user_id>/block/', UserBlockView.as_view(), name='user-block'),
    
    # professional related
    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<uuid:pk>/verify/', AdminVerifyProfessionalView.as_view(), name='verify-professional'),
    path('professional/verification/requests/', ProfessionalVerificationRequestListView.as_view(), name='professional-verification-request'),
    
    #customer related
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    
    
    #service post related
    path('services/reported-posts/', AdminServicePostReportListView.as_view(), name='servicepost-report-list'),
    path('services/<uuid:service_post_id>/delete/', AdminDeleteReportedPostView.as_view(), name='admin-delete-reported-post'),
    
    #admin related
    path('admins/', AdminListView.as_view(), name='admin-list'),

    #stat related
    path('stats/', StatisticsView.as_view(), name='user-stats'),
    
    
]
