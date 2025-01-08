# from django.contrib import admin
# from .models import User, AdminProfile, CustomerProfile, ProfessionalProfile, Education, Portfolio, Certificate, Address
# from django.contrib.auth.admin import UserAdmin
# from django.utils.translation import gettext_lazy as _


# # Custom User Admin
# class CustomUserAdmin(UserAdmin):
#     model = User
#     list_display = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number', 'user_type', 'is_active', 'is_staff', 'is_superuser')
#     list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')
#     search_fields = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number')
#     ordering = ('email',)
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'phone_number')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {'fields': ('email', 'password1', 'password2')}),
#         (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'phone_number')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type')}),
#     )


# # Admin Profile Admin
# class AdminProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'permissions', 'admin_level')
#     search_fields = ('user__email', 'permissions', 'admin_level')
#     list_filter = ('admin_level',)


# # Customer Profile Admin
# class CustomerProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'rating', 'total_interactions')
#     search_fields = ('user__email', 'rating')
#     list_filter = ('rating',)


# # Professional Profile Admin
# class ProfessionalProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'is_verified', 'business_logo', 'business_card', 'rating', 'years_of_experience', 'portfolio_url', 'availability')
#     search_fields = ('user__email', 'business_logo', 'business_card', 'portfolio_url')
#     list_filter = ('is_verified', 'availability', 'rating')


# # Education Admin
# class EducationAdmin(admin.ModelAdmin):
#     list_display = ('school', 'degree', 'field_of_study', 'location', 'start_date', 'end_date', 'is_current_student')
#     search_fields = ('school', 'degree', 'field_of_study')
#     list_filter = ('is_current_student',)


# # Portfolio Admin
# class PortfolioAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description','image', 'created_at', 'updated_at')
#     search_fields = ('title', 'description')
#     list_filter = ('created_at', 'updated_at')


# # Certificate Admin
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ('name', 'issued_by', 'document_url', 'date_issued', 'expiration_date', 'certificate_type', 'is_renewable')
#     search_fields = ('name', 'issued_by', 'certificate_type')
#     list_filter = ('is_renewable', 'date_issued', 'expiration_date')


# # Address Admin
# class AddressAdmin(admin.ModelAdmin):
#     list_display = ('user', 'country', 'region', 'woreda', 'city', 'kebele', 'street', 'latitude', 'longitude', 'is_current')
#     search_fields = ('user__email', 'country', 'region', 'city', 'street')
#     list_filter = ('is_current',)


# # Register the models with the custom admin classes
# admin.site.register(User, CustomUserAdmin)
# admin.site.register(AdminProfile, AdminProfileAdmin)
# admin.site.register(CustomerProfile, CustomerProfileAdmin)
# admin.site.register(ProfessionalProfile, ProfessionalProfileAdmin)
# admin.site.register(Education, EducationAdmin)
# admin.site.register(Portfolio, PortfolioAdmin)
# admin.site.register(Certificate, CertificateAdmin)
# admin.site.register(Address, AddressAdmin)
