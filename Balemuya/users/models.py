from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Custom User Manager
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

# User Types
USER_TYPE_CHOICES = (
    ('customer', 'Customer'),
    ('professional', 'Professional'),
    ('admin', 'Admin'),
)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
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
    bio = models.TextField(blank=True, null=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'phone_number']

    objects = CustomUserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def __str__(self):
        return self.email

# Address Model
class Address(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
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

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

# Permissions Model
class Permission(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

# Admin Profile Model
class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    permissions = models.ManyToManyField(Permission, blank=True, related_name='admins')
    admin_level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - Admin Level {self.admin_level}"

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def has_perm(self, perm):
        return self.permissions.filter(name=perm).exists()

# Admin Action Log
class AdminLog(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    admin = models.ForeignKey(AdminProfile, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.user.email} - {self.action}"

    class Meta:
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'

# Customer Profile
class CustomerProfile(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_interactions = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

# Skill Model for Professionals
class Skill(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

# Professional Profile
class ProfessionalProfile(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    skills = models.ManyToManyField(Skill, blank=True,null=True, related_name='professionals')
    is_verified = models.BooleanField(default=False)
    business_logo = models.ImageField(upload_to='professional_logos', null=True, blank=True)
    business_card = models.ImageField(upload_to='business_cards', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    portfolio_url = models.URLField(null=True, blank=True)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Professional'
        verbose_name_plural = 'Professionals'

# Education Model for Professionals
class Education(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    document_url = models.URLField(null=True, blank=True, unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(null=True, blank=True)
    honors = models.CharField(max_length=255, blank=True, null=True)
    is_current_student = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.school} - {self.degree}"

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'
        ordering = ['-start_date']

# Portfolio Model for Professionals
class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='portfolios')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio_images', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        ordering = ['-created_at']

# Certificate Model for Professionals
class Certificate(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=100)
    issued_by = models.CharField(max_length=100)
    document_url = models.URLField()
    date_issued = models.DateField()
    expiration_date = models.DateField()
    certificate_type = models.CharField(max_length=100, blank=True, null=True)
    is_renewable = models.BooleanField(default=False)
    renewal_period = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
