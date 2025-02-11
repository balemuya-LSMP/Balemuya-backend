from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()

class Notification(models.Model):
    TYPE_CHOICES = [
    ('info','info'),
    ('new_job', 'New Job Post'),
    ('job_apply', 'Job Application'),
    ('verify_request', 'Verification Request'),
    ('verify_response', 'Verification Response'),
    ('new_booking', 'New Booking'),
    ('new_job_request', 'New Job Request'),
    ('new_job_response', 'Job Request Response'),
    ('new_complain', 'New Complaint'),
    ('new_feedback', 'New Feedback'),
    ('new_review', 'New Review'),
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
