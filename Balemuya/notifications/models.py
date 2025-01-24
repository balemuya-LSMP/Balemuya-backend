from django.db import models
from users.models import User

# Create your models here.


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_info = f"from {self.sender}" if self.sender else "from System"
        return f"Notification for {self.recipient} {sender_info}: {self.message[:20]}"
