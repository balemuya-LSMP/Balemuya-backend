from django.contrib import admin
from .models import (
    Address,
    User,
    Customer,
    Professional,
    Feedback,
    Permission,
    Admin,
    AdminLog,
    Skill,
    Education,
    Portfolio,
    Certificate,
    SubscriptionPlan,
    Payment,
    SubscriptionPayment,
    VerificationRequest,
)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('country', 'region', 'city', 'latitude', 'longitude')
    search_fields = ('country', 'region', 'city')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email','username', 'phone_number', 'user_type','entity_type','is_active', 'is_email_verified','is_phone_verified',)
    search_fields = ('email', 'phone_number')
    list_filter = ('user_type', 'is_active')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name','gender','number_of_employees' ,'number_of_services_booked', 'rating')
    search_fields = ('user__email', 'full_name',)



@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name','gender', 'years_of_experience', 'rating')
    search_fields = ('user__email','full_name')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'rating', 'created_at')
    search_fields = ('user__email', 'message')
    list_filter = ('rating',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_level')
    search_fields = ('user__email', 'first_name', 'last_name')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'timestamp')
    search_fields = ('admin__user__email', 'action')
    list_filter = ('timestamp',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('professional', 'school', 'degree', 'created_at')
    search_fields = ('professional__user__email', 'school')
    list_filter = ('created_at',)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('professional', 'title', 'created_at')
    search_fields = ('professional__user__email', 'title')
    list_filter = ('created_at',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('professional', 'name', 'created_at')
    search_fields = ('professional__user__email', 'name')
    list_filter = ('created_at',)

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('professional', 'status', 'created_at', 'updated_at')
    search_fields = ('professional__user__email',)
    list_filter = ('status',)
    
    
#payment related
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('professional', 'plan_type', 'duration', 'cost', 'start_date', 'end_date', 'is_expired')
    search_fields = ('professional__email', 'plan_type')
    list_filter = ('plan_type', 'duration')
    ordering = ('-start_date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'customer', 'professional', 'service', 'amount', 'payment_date', 'payment_status')
    search_fields = ('transaction_id', 'customer__email', 'professional__email')
    list_filter = ('payment_status', 'payment_method')
    ordering = ('-payment_date',)

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'subscription_plan', 'professional', 'amount', 'payment_date', 'payment_status')
    search_fields = ('transaction_id', 'professional__email', 'subscription_plan__professional__email')
    list_filter = ('payment_status',)
    ordering = ('-payment_date',)