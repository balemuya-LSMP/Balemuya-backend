from django.contrib import admin
from .models import ServicePost, ServicePostApplication, ServiceBooking

@admin.register(ServicePost)
class ServicePostAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'category', 'description', 'status', 'urgency', 'work_due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('id', 'description', 'customer__user__username', 'category__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(ServicePostApplication)
class ServicePostApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'professional', 'message', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'service__category', 'created_at')
    search_fields = ('id', 'service__id', 'professional__user__username', 'message')
    ordering = ('-created_at',)
    autocomplete_fields = ('service', 'professional')


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'scheduled_date', 'agreed_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('id', 'application__service__id', 'application__professional__user__username')
    ordering = ('-created_at',)
    autocomplete_fields = ('application',)
