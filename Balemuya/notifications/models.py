from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()

class Notification(models.Model):
    # Expanded Notification Types for Your Platform
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('system', 'System'),  # System-generated notifications
        ('service_post', 'Service Post'),  # Notification related to a new service post
        ('service_request', 'Service Request'),  # Notification related to service requests
        ('payment', 'Payment'),  # Notifications related to payments
        ('application', 'Application'),  # Notifications about applications (e.g., job, project)
        ('status_update', 'Status Update'),  # Status updates for services or applications
        ('message', 'Message'),  # Direct messages between users
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ManyToManyField(User, related_name='notifications', blank=True)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications'
    )
    title = models.CharField(max_length=255,blank=True,null=True)
    message = models.TextField() 
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    url = models.URLField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        sender_info = f"from {self.sender}" if self.sender else "from System"
        return f"Notification of {self.notification_type} ,{sender_info}: {self.title[:20]}"

    class Meta:
        ordering = ['-created_at']  # Show recent notifications first
