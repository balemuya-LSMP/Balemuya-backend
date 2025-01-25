from django.db import models
import uuid
from users.models import Customer,Professional
from common.models import Category
from users.models import Address

# Create your models here.

class ServicePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='services')
    description = models.TextField(null=True, blank=True)  
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ], default='active') 
    urgency = models.CharField(max_length=10, choices=[
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('high', 'High'),
    ], default='normal') 
    work_due_date = models.DateTimeField(null=True, blank=True)
    location = models.OneToOneField(Address, on_delete=models.CASCADE,default=None, related_name='service_post')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return f'Service {self.id} by {self.customer} in {self.category} (Urgency: {self.urgency})'
    



class ServicePostApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(ServicePost, on_delete=models.CASCADE, related_name='applications')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Application {self.id} for {self.service} by {self.professional} (Status: {self.status})'
    
    
class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(
        ServicePostApplication, 
        on_delete=models.CASCADE, 
        related_name='booking'
    )
    scheduled_date = models.DateTimeField()
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Booking {self.id} for {self.application.service} by {self.application.professional} (Status: {self.status}, Price: {self.agreed_price})'