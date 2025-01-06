from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

USER_TYPE_CHOICES = (
    ('customer', 'Customer'),
    ('professional', 'Professional'),
    ('admin', 'Admin'),
)

class User(AbstractUser):
    username = None 
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=30, choices=[('male', 'Male'), ('female', 'Female')])
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    kebele_id_image = models.ImageField(upload_to='kebele_id_images', null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_addresses')
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    woreda = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True, blank=True)
    kebele = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.country}, {self.region}, {self.woreda}, {self.city}, {self.street}"