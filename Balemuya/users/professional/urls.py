from django.urls import path 
import uuid
from .views import ProfessionalProfileView, ProfessionalProfileUpdateView,ProfessionalSkillView,ProfessionalCategoryView,CertificateView,EducationView,PortfolioView,\
    ProfessionalVerificationRequestView,InitiatePaymentView,CheckPaymentView,ProfessionalSubscriptionHistoryView,\
    ProfessionalServiceListView,ProfessionalServiceRequestsAPIView,ServicePostSearchView,ServicePostFilterView

urlpatterns = [
    path('<uuid:pk>/profile/',ProfessionalProfileView.as_view(), name='professional-profile'),
    path('profile/update/',ProfessionalProfileUpdateView.as_view(), name='professional-update'),
    path('profile/skills/', ProfessionalSkillView.as_view(), name='skill-create-update-delete'),
    path('profile/categories/', ProfessionalCategoryView.as_view(), name='category-create-remove'),
    
    path('profile/certificates/add/', CertificateView.as_view(), name='certificate-create'),  # POST
    path('profile/certificates/<uuid:pk>/update/', CertificateView.as_view(), name='certificate-update'),  # PUT
    path('profile/certificates/<uuid:pk>/delete/', CertificateView.as_view(), name='certificate-delete'),  # DELETE
    
    path('profile/educations/add/', EducationView.as_view(), name='education-create'),  # POST
    path('profile/educations/<uuid:pk>/update/', EducationView.as_view(), name='education-update'),  # PUT
    path('profile/educations/<uuid:pk>/delete/', EducationView.as_view(), name='education-delete'),  # DELETE
    
    path('profile/portfolios/add/', PortfolioView.as_view(), name='portfolio-create'),  # POST
    path('profile/portfolios/<uuid:pk>/update/', PortfolioView.as_view(), name='portfolio-update'),  # PUT
    path('profile/portfolios/<uuid:pk>/delete/', PortfolioView.as_view(), name='portfolio-delete'),  # DELETE
    path('verification-requests/', ProfessionalVerificationRequestView.as_view(), name='professional-verification-request'),
    path('subscription/history/',ProfessionalSubscriptionHistoryView.as_view(), name='professional-subscription-history'),
    
    #services
    path('services/', ProfessionalServiceListView.as_view(), name='professional-service-app-list'),
    path('service/search/', ServicePostSearchView.as_view(), name='service_post_search'),
    path('service/filter/', ServicePostFilterView.as_view(), name='service_post_filter'),

    path('service-requests/', ProfessionalServiceRequestsAPIView.as_view(), name='professional_service_requests'),#professional srvices requested

    #payment related
    path('subscription/payment/initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('subscription/payment/check/<str:transaction_id>/', CheckPaymentView.as_view(), name='check_payment'),
]