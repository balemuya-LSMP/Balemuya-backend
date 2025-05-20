from django.contrib import admin
from .models import ServicePost, ServicePostApplication, ServiceBooking,Review,Complain,ServicePostReport,ServiceRequest

@admin.register(ServicePost)
class ServicePostAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'category', 'description', 'status', 'urgency', 'work_due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('id', 'description',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'professional', 'detail', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('id', 'detail','status')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    



@admin.register(ServicePostApplication)
class ServicePostApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'professional', 'message', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'service__category', 'created_at')
    search_fields = ('id', 'service__id', 'professional__user__username', 'message')
    ordering = ('-created_at',)
    autocomplete_fields = ('service',)


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'scheduled_date', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('id', 'status',)
    ordering = ('-created_at',)
    autocomplete_fields = ('application',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('id', 'comment','rating')
    ordering = ('-created_at',)
    autocomplete_fields = ('booking',)

@admin.register(Complain)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'user', 'message', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'message','status')
    ordering = ('-created_at',)
    autocomplete_fields = ('booking', 'user')
    
    

@admin.register(ServicePostReport)
class ServicePostReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_post', 'reporter', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('id', 'reason')
    ordering = ('-created_at',)
    autocomplete_fields = ('service_post', 'reporter')