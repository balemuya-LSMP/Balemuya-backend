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
        ('verification_request', 'Verification Request'),
        ('system', 'System'),
        ('service_post', 'Service Post'),
        ('service_request', 'Service Request'),
        ('payment', 'Payment'),
        ('application', 'Application'),
        ('status_update', 'Status Update'),
        ('message', 'Message'), 
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ManyToManyField(User, related_name='notifications', blank=True)
    title = models.CharField(max_length=255,blank=True,null=True)
    message = models.TextField() 
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    url = models.URLField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):

        return f"Notification of {self.notification_type} : {self.title[:20]}"

    class Meta:
        ordering = ['-created_at']
