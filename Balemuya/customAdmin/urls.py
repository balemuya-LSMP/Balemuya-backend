from django.urls import path
import uuid
from .views import ProfessionalListView,CustomerListView,AdminListView

from .views import (
    ProfessionalListView,
    AdminVerifyProfessionalView,
    CustomerListView,
    AdminListView
    
)

urlpatterns = [
    # List all professionals
    path('professionals/', ProfessionalListView.as_view(), name='professional-list'),
    path('professionals/<uuid:id>/verify/', AdminVerifyProfessionalView.as_view(), name='verify-professional'),
    # path('professionals/<uuid:id>/update/', ProfessionalUpdateView.as_view(), name='professional-update'),
    # path('professionals/<uuid:id>/delete/', ProfessionalDeleteView.as_view(), name='professional-delete'),
    
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    # path('customers/<uuid:id>/', CustomerDetailView.as_view(), name='customer-detail'),
    # path('customers/create/', CustomerCreateView.as_view(), name='customer-create'),
    # path('customers/<uuid:id>/update/', CustomerUpdateView.as_view(), name='customer-update'),
    # path('customers/<uuid:id>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
    
    path('admins/', AdminListView.as_view(), name='admin-list'),
#     path('admins/<uuid:id>/', AdminDetailView.as_view(), name='admin-detail'),
#     path('admins/create/', AdminCreateView.as_view(), name='admin-create'),
#     path('admins/<uuid:id>/update/', AdminUpdateView.as_view(), name='admin-update'),
#     path('admins/<uuid:id>/delete/', AdminDeleteView.as_view(), name='admin-delete'),
# 
# 
]