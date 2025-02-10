from django.db import models
import uuid
from users.models import Customer,Professional
from common.models import Category
from users.models import Address, User

# Create your models here.

class ServicePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100,null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='services')
    description = models.TextField(null=True, blank=True)  
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('booked', 'booked'),
        ('completed', 'Completed'),
        ('canceled','Canceled')
    ], default='active') 
    urgency = models.CharField(max_length=10, choices=[
        ('normal', 'Normal'),
        ('urgent', 'Urgent')
    ], default='normal') 
    work_due_date = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Address, on_delete=models.CASCADE,default=None, related_name='service_post')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return f'Service {self.title} by {self.customer} in {self.category} (Urgency: {self.urgency})'
    



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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Booking {self.id} for {self.application.service} by {self.application.professional} (Status: {self.status})'
    
class Complain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ServiceBooking, on_delete=models.CASCADE, related_name='complains')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complains')
    message = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Complain'
        verbose_name_plural = 'Complains'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Complain {self.id} for {self.booking} by {self.user} (Status: {self.status})'
    
    
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ServiceBooking, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Review {self.id} for {self.booking} by {self.user} (Rating: {self.rating})'
    