from django.contrib import admin
from .models import User, AdminProfile, CustomerProfile, ProfessionalProfile, Education, Portfolio, Certificate, Address, Skill
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1 

class EducationInline(admin.StackedInline):
    model = Education
    extra = 1


class SkillsInline(admin.StackedInline):
    model = ProfessionalProfile.skills.through
    extra = 1


class PortfolioInline(admin.StackedInline):
    model = Portfolio
    extra = 1


class CertificateInline(admin.StackedInline):
    model = Certificate
    extra = 1

# Custom User Admin
class CustomUserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    inlines = [AddressInline]


# Admin Profile Admin
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_level')
    search_fields = ('user__email', 'admin_level')
    list_filter = ('admin_level',)


# Customer Profile Admin
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    search_fields = ('user__email', 'rating')
    list_filter = ('rating',)


# Professional Profile Admin
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'business_logo', 'business_card', 'rating', 'years_of_experience', 'portfolio_url', 'availability')
    search_fields = ('user__email', 'business_logo', 'business_card', 'portfolio_url')
    list_filter = ('is_verified', 'availability', 'rating')
    inlines = [EducationInline, SkillsInline, PortfolioInline, CertificateInline]  


# Register the models with the custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(AdminProfile, AdminProfileAdmin)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(ProfessionalProfile, ProfessionalProfileAdmin)
admin.site.register(Education) 
admin.site.register(Skill)
admin.site.register(Portfolio)
admin.site.register(Certificate) 
admin.site.register(Address)
