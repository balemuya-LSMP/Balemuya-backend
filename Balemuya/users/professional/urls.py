from django.urls import path 
import uuid
from .views import ProfessionalProfileView, ProfessionalProfileUpdateView,ProfessionalSkillView,ProfessionalCategoryView,CertificateView,EducationView,PortfolioView,\
    ProfessionalVerificationRequestView,InitiateSubscriptionPaymentView,CheckPaymentView,ProfessionalSubscriptionHistoryView,\
    ProfessionalServiceListView,ProfessionalServiceRequestsAPIView,ServiceRequestAcceptAPIView,ServiceRequestRejectAPIView,ServiceRequestCompleteAPIView,ServicePostSearchView,ServicePostFilterView,ProfessionalPaymentWithdrawalView,\
        ProfessionalBankAccountView,BankListView

urlpatterns = [
    path('<uuid:pk>/profile/',ProfessionalProfileView.as_view(), name='professional-profile'),
    path('profile/update/',ProfessionalProfileUpdateView.as_view(), name='professional-update'),
    path('profile/skills/', ProfessionalSkillView.as_view(), name='skill-create-update-delete'),
    path('profile/categories/', ProfessionalCategoryView.as_view(), name='category-create-remove'),
    
    path('bank-lists/',BankListView.as_view(), name='bank-list'),
    path('bank-account/',ProfessionalBankAccountView.as_view(), name='professional-bank-account'),
    
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
    path('service/search/', ServicePostSearchView.as_view(), name='service-post-search'),
    path('service/filter/', ServicePostFilterView.as_view(), name='service-post-filter'),

    path('service-requests/', ProfessionalServiceRequestsAPIView.as_view(), name='professional-service-requests'),
    path('service-requests/<uuid:req_id>/accept/', ServiceRequestAcceptAPIView.as_view(), name='service-request-accept'),
    path('service-requests/<uuid:req_id>/reject/', ServiceRequestRejectAPIView.as_view(), name='service-request-reject'),
    path('service-requests/<uuid:req_id>/complete/', ServiceRequestCompleteAPIView.as_view(), name='service-request-complete'),

    #payment related
    path('subscription/payment/initiate/', InitiateSubscriptionPaymentView.as_view(), name='initiate_subscription-payment'),
    path('subscription/payment/check/<str:transaction_id>/', CheckPaymentView.as_view(), name='check_payment'),
    
    
    path('services/payment/withdraw/', ProfessionalPaymentWithdrawalView.as_view(), name='professional-withdrawal'),
    
]