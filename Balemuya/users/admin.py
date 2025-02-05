from django.contrib import admin
from django.utils.html import mark_safe
from .models import User, Admin, Customer, Professional, Education, Portfolio, Certificate, Address, Skill, Payment, SubscriptionPlan,\
    VerificationRequest,Feedback
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.conf import settings


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

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message','created_at')
    search_fields = ('user__email',)
    list_filter = ('created_at',)

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('email', 'first_name', 'middle_name', 'last_name','profile_image_preview', 'phone_number', 'gender', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'middle_name', 'last_name', 'phone_number')
    ordering = ('email',)
    
    inlines = [AddressInline]
    
    def profile_image_preview(self, obj):
            return mark_safe(f'<img src="{settings.MEDIA_URL}{obj.profile_image}" width="50" height="50" />')
    profile_image_preview.allow_tags = True
    profile_image_preview.short_description = 'Profile Image'

# Admin Admin
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_level')
    search_fields = ('user__email', 'admin_level')
    list_filter = ('admin_level',)

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating','number_of_services_booked')
    search_fields = ('user__email', 'rating')
    list_filter = ('rating',)

# Professional Admin
@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'kebele_id_image_front_preview', 'kebele_id_image_back_preview', 'rating', 'years_of_experience', 'is_available')
    search_fields = ('user__email',)
    list_filter = ('is_verified', 'is_available', 'rating')

    def kebele_id_image_front_preview(self, obj):
            return mark_safe(f'<img src="{settings.MEDIA_URL}{obj.kebele_id_front_image}" width="50" height="50" />')
    kebele_id_image_front_preview.allow_tags = True
    kebele_id_image_front_preview.short_description = 'Id front Image'

    def kebele_id_image_back_preview(self, obj):
            return mark_safe(f'<img src="{settings.MEDIA_URL}{obj.kebele_id_back_image}" width="50" height="50" />')
    kebele_id_image_back_preview.allow_tags = True
    kebele_id_image_back_preview.short_description = 'Id back Image'
    inlines = [EducationInline, SkillsInline, PortfolioInline, CertificateInline]  

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('professional', 'plan_type', 'duration', 'cost', 'start_date', 'end_date', 'is_expired')
    list_filter = ('plan_type', 'duration')
    search_fields = ('professional__name', 'plan_type')
    readonly_fields = ('start_date', 'end_date', 'is_expired')

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('professional', 'subscription_plan', 'amount', 'payment_status', 'payment_method', 'payment_date')
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('professional__name', 'payment_status', 'subscription__plan_type')
    readonly_fields = ('payment_date',)


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('professional', 'status', 'verified_by', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('professional__name', 'verified_by__name')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('professional', 'degree', 'field_of_study')
    list_filter = ('degree', 'field_of_study')
    search_fields = ('professional__name', 'degree', 'field_of_study')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('professional', 'title', 'description', 'image_preview')
    search_fields = ('professional__name', 'title', 'description')

    def image_preview(self, obj):
            return mark_safe(f'<img src="{settings.MEDIA_URL}{obj.image}" width="50" height="50" />')
    image_preview.allow_tags = True
    image_preview.short_description = 'Image'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('professional','image_preview')
    search_fields = ('professional__name',)
    
    def image_preview(self, obj):
            return mark_safe(f'<img src="{settings.MEDIA_URL}{obj.image}" width="50" height="50" />')
    image_preview.allow_tags = True
    image_preview.short_description = 'Image'
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'region', 'city', 'latitude', 'longitude') 
    search_fields = ('user__email', 'country', 'region', 'city')
    


# Register the models with the custom admin classes
# admin.site.register(User, CustomUserAdmin)
# admin.site.register(Admin, AdminAdmin)
# admin.site.register(Customer, CustomerAdmin)
# admin.site.register(Professional, ProfessionalAdmin)
# admin.site.register(Education) 
# admin.site.register(Skill)
# admin.site.register(Portfolio)
# admin.site.register(Certificate) 
# admin.site.register(Address)
# admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
# admin.site.register(Payment, PaymentAdmin)
