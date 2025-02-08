from django.contrib import admin
from .models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (  'message_summary', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message')
    readonly_fields = ('created_at',)
    
    def message_summary(self, obj):
        """Shortens the message for easier display in the admin panel."""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_summary.short_description = 'Message Summary'