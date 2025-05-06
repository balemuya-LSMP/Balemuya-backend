from django.urls import path,include
import uuid
from .user.views import (UserListView,UserCreateView,UserDetailView,UserBlockView,ProfessionalListView,CustomerListView,AdminListView,AdminVerifyProfessionalView,
ProfessionalVerificationRequestListView)
from .service.views import (AdminServicePostListView,AdminServicePostDetailView,AdminServicePostReportListView,AdminDeleteReportedPostView,AdminServicePostReportDetailView,
                            AdminServicePostSearchView,AdminToggleServicePostStatusView)

from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    StatisticsView  
    
)

urlpatterns = [
    
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list'), #manage categories
    path('categories/<uuid:category_id>/', CategoryDetailView.as_view(), name='category-update'),
    
    # basic user related 
    path('users/', UserListView.as_view(), name='user-list'), 
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user-update'),
    path('users/<uuid:user_id>/block/', UserBlockView.as_view(), name='user-block'),
    
    # professional related
    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<uuid:ver_req_id>/verify/', AdminVerifyProfessionalView.as_view(), name='verify-professional'),
    path('professional/verification/requests/', ProfessionalVerificationRequestListView.as_view(), name='professional-verification-request'),
    
    #customer related
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    
    
   # service post related (admin side)
path('services/', AdminServicePostListView.as_view(), name='servicepost-list'),
path('services/reported-posts/', AdminServicePostReportListView.as_view(), name='servicepost-report-list'),
path('services/<uuid:service_post_id>/delete/', AdminDeleteReportedPostView.as_view(), name='admin-delete-reported-post'),

# Additional useful endpoints
path('services/<uuid:service_post_id>/', AdminServicePostDetailView.as_view(), name='admin-servicepost-detail'),
path('services/<uuid:service_post_id>/toggle-active/', AdminToggleServicePostStatusView.as_view(), name='admin-toggle-servicepost-status'),
path('services/<uuid:service_post_id>/reports/', AdminServicePostReportDetailView.as_view(), name='admin-servicepost-report-detail'),
path('services/search/', AdminServicePostSearchView.as_view(), name='admin-servicepost-search'),
    
    #admin related
    path('admins/', AdminListView.as_view(), name='admin-list'),

    #stat related
    path('stats/', StatisticsView.as_view(), name='user-stats'),
    
    
]
