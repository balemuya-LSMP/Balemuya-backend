from django.contrib import admin
from .models import User, Address, Professional, Certificate, Portfolio, Education, Skill

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1 
    fields = ['country', 'region', 'woreda', 'city', 'kebele', 'street', 'latitude', 'longitude', 'is_current']  

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'middle_name', 'last_name',
        'phone_number', 'gender', 'profile_image', 'kebele_id_image',
        'user_type', 'is_active', 'is_superuser'
    ]
    list_filter = [
        'user_type', 'email', 'first_name', 'middle_name',
        'last_name', 'phone_number', 'gender', 'is_active'
    ]
    search_fields = [
        'email', 'first_name', 'middle_name', 'last_name',
        'phone_number', 'gender'
    ]
    inlines = [AddressInline] 

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'country', 'region', 'woreda', 
        'city', 'kebele', 'street', 'latitude', 
        'longitude', 'is_current'
    ]
    search_fields = [
        'country', 'region', 'woreda', 'city', 
        'kebele', 'street'
    ]
    
class EducationInline(admin.StackedInline):
    model = Education
    extra = 1
    fields = [
        'school', 'degree', 'field_of_study',
        'location', 'document_url', 'start_date', 'end_date',
        'honors', 'is_current_student'
    ]
    
class PortfolioInline(admin.StackedInline):
    model = Portfolio
    extra = 1
    fields = [
        'title', 'description', 'image', 'video_url'
    ]
    
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']

class CertificateInline(admin.StackedInline):
    model = Certificate
    extra = 1
    fields = [
        'name', 'issued_by', 'document_url', 'date_issued',
        'expiration_date', 'certificate_type', 'is_renewable',
        'renewal_period'
    ]

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'is_verified', 'is_approved',
        'logo', 'business_card', 'rating', 'years_of_experience',
        'portfolio_url', 'availability'
    ]
    search_fields = [
        'email', 'skills__name', 'is_verified', 'is_approved',
        'logo', 'business_card', 'rating', 'years_of_experience',
        'portfolio_url', 'availability'
    ]
    filter_horizontal = ['skills']
    inlines = [CertificateInline, PortfolioInline, EducationInline]  

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = [
        'professional', 'school', 'degree', 'field_of_study',
        'location', 'document_url', 'start_date', 'end_date',
        'honors', 'is_current_student'
    ]
    search_fields = [
        'professional__email', 'school', 'degree', 'field_of_study',
        'location', 'document_url', 'start_date', 'end_date',
        'honors', 'is_current_student'
    ]
    
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'professional', 'title', 'description', 'image', 'video_url'
    ]
    search_fields = [
        'professional__email', 'title', 'description'
    ]

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        'professional', 'name', 'issued_by', 'document_url', 'date_issued',
        'expiration_date', 'certificate_type', 'is_renewable',
        'renewal_period'
    ]
    search_fields = [
        'professional__email', 'name', 'issued_by', 'document_url', 'date_issued',
        'expiration_date', 'certificate_type', 'is_renewable',
        'renewal_period'
    ]

