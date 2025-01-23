from django.db import models
import uuid
from users.models import Customer

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name
    
    

class Service(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    def __str__(self):
        return f'Service {self.id} by {self.customer} in {self.category} (Urgency: {self.urgency})'