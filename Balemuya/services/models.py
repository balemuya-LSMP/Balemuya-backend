from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from common.models import Category

# Create your models here.

class ServicePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE, related_name='service_posts')
    title = models.CharField(max_length=100,null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='service_posts')
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
    location = models.ForeignKey('users.Address', on_delete=models.CASCADE,default=None, related_name='service_post')

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
    service = models.ForeignKey(ServicePost, on_delete=models.CASCADE, related_name='service_applications')
    professional = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='professional_applications')
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
        'ServicePostApplication', 
        on_delete=models.CASCADE, 
        related_name='service_booking'
    )
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Booking {self.id} for {self.application.service} by {self.application.professional} (Status: {self.status})'
    
    
    
class ServiceRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('users.User', related_name='service_recieved', on_delete=models.CASCADE)
    professional = models.ForeignKey('users.User', related_name='service_requests', on_delete=models.CASCADE)
    detail = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'),('cancled','canceled') ,('accepted', 'Accepted'), ('rejected', 'Rejected')],default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    
    def __str__(self):
        
        return f"ServiceRequest {self.id} - {self.status} for {self.customer}"

    class Meta:
        ordering = ['-created_at'] 
        verbose_name = "Service Request"
        verbose_name_plural = "Service Requests"
    

class Complain(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey('ServiceBooking', on_delete=models.CASCADE, related_name='complains', null=True, blank=True)
    service_request = models.ForeignKey('ServiceRequest', on_delete=models.CASCADE, related_name='complains', null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='complains')
    message = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Complain'
        verbose_name_plural = 'Complains'
        ordering = ['-created_at']

    def __str__(self):
        return f'Complain {self.id} by {self.user.username} (Status: {self.status})'

    def clean(self):
        """Ensure a complaint is linked to either a booking or a service request."""
        if not self.booking and not self.service_request:
            raise ValidationError("A complaint must be linked to either a booking or a service request.")

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey('ServiceBooking', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    service_request = models.ForeignKey('ServiceRequest', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f'Review {self.id} by {self.user.username} (Rating: {self.rating})'

    def clean(self):
        """Ensure a review is linked to either a booking or a service request."""
        if not self.booking and not self.service_request:
            raise ValidationError("A review must be linked to either a booking or a service request.")