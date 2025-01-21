from django.contrib import admin
from .models import User, Admin, Customer, Professional, Education, Portfolio, Certificate, Address, Skill,Payment,SubscriptionPlan
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1 

class EducationInline(admin.StackedInline):
    model = Education
    extra = 1

class SkillsInline(admin.StackedInline):
    model = Professional.skills.through
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
    list_display = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number','gender', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    inlines = [AddressInline]
# Admin Admin
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_level')
    search_fields = ('user__email', 'admin_level')
    list_filter = ('admin_level',)

# Customer Admin
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    search_fields = ('user__email', 'rating')
    list_filter = ('rating',)

# Professional Admin
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'profile_image', 'kebele_id_front_image', 'kebele_id_back_image', 'rating', 'years_of_experience', 'is_available')
    search_fields = ('user__email',)
    list_filter = ('is_verified', 'is_available', 'rating')
    inlines = [EducationInline, SkillsInline, PortfolioInline, CertificateInline]  
    
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('professional', 'plan_type', 'duration', 'cost', 'start_date', 'end_date', 'is_expired')
    list_filter = ('plan_type', 'duration')
    search_fields = ('professional__name', 'plan_type')
    readonly_fields = ('start_date', 'end_date', 'is_expired')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('professional', 'subscription', 'amount', 'payment_status', 'payment_method', 'payment_date')
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('professional__name', 'payment_status', 'subscription__plan_type')
    readonly_fields = ('payment_date',)

# Register the models with the custom admin classes
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Customer)
admin.site.register(Professional)
admin.site.register(Education) 
admin.site.register(Skill)
admin.site.register(Portfolio)
admin.site.register(Certificate) 
admin.site.register(Address)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Payment, PaymentAdmin)