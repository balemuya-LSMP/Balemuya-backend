from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from decimal import Decimal


# Address Model
class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100, default='Ethiopia')
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    def __str__(self):
        return f"{self.country}, {self.region}, {self.city}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

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
ACCOUNT_TYPE_CHOICES = [
    ('organization', 'Organization'),
    ('individual', 'Individual'),
]
USER_TYPE_CHOICES = [
    ('customer', 'Customer'),
    ('professional', 'Professional'),
    ('admin', 'Admin'),
]

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=30)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    profile_image = CloudinaryField('image', null=True, blank=True, folder='Profile/profile_images')
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)

    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPE_CHOICES, default='ind')

    is_active = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
##############  Abstract Base Individual Mixin  ############################
class BaseCustomerMixin(models.Model):
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    number_of_services_booked = models.PositiveIntegerField(default=0)    
    class Meta:
        abstract = True
    
###############        Individual customer  Mixin ###########################
class Customer(BaseCustomerMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    first_name = models.CharField(max_length=30,null=True,blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')],null=True,blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Individual Customer'
        verbose_name_plural = 'Individual Customers'
    
    def __str__(self):
        return self.user.email
    
    
############## Organizational Customer model ##########################
class OrgCustomer(BaseCustomerMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='org_customer')
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    number_of_employees = models.PositiveIntegerField(null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True) 
    logo = CloudinaryField('image', null=True, blank=True, folder='Org_customer/logos')
    
    def __str__(self):
        return self.organization_name
    
###############  Base professional Mixin ###########################
class BaseProfessionalMixin(models.Model):
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    skills = models.ManyToManyField('Skill', blank=True, related_name='%(class)s_professionals')
    categories = models.ManyToManyField(
        'common.Category', blank=True, related_name='%(class)s_professionals'
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    num_of_request = models.IntegerField(default=0)

    class Meta:
        abstract = True


class Professional(BaseProfessionalMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional')
    first_name = models.CharField(max_length=30,blank=True,null =True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    gender = models.CharField(choices=[('male','Male'),('female','Female')],null=True)
    
    kebele_id_front_image = CloudinaryField(
        'image', null=True, blank=True, folder='Professional/kebele_id_images/front_images'
    )
    kebele_id_back_image = CloudinaryField(
        'image', null=True, blank=True, folder='Professional/kebele_id_images/back_images'
    )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Professional'
        verbose_name_plural = 'Professionals'

############## Organizational Professional model ##########################
class OrgProfessional(BaseProfessionalMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='org_professional')
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    number_of_employees = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True) 
    logo = CloudinaryField('image', null=True, blank=True, folder='Org_professional/logos')
    
    def __str__(self):
        return self.organization_name
    
################## Feedback  model #####################
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    rating = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

###################  Permission Model   ##########################
class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'


##########################  Admin Model #############################
class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    first_name = models.CharField(max_length=30,null=True,blank=True)
    last_name = models.CharField(max_length=30,null=True,blank=True)
    gender = models.CharField(max_length=30, choices=[('male', 'Male'), ('female', 'Female')],null=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='admins')
    admin_level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - Admin Level {self.admin_level}"

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def has_perm(self, perm):
        return self.permissions.filter(name=perm).exists()


############# Admin Action Log ########################
class AdminLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.user.email} - {self.action}"

    class Meta:
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'


############### Skill Model for Professionals ##########################
class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


##################3 Education Model for Professionals ###################
class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='educations'  # Updated to use CustomUser
    )
    school = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user_type != 'professional':
            raise ValueError("Only professionals can have education records.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school} - {self.degree or 'N/A'}"

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'
        ordering = ['-created_at']

class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='portfolios'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True, folder='PortfolioImages/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user_type != 'professional':
            raise ValueError("Only professionals can create portfolios.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        ordering = ['-created_at']



# Certificate Model for Professionals
class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='certificates'  # Updated to use CustomUser
    )
    image = CloudinaryField(
        'certificate_image', null=True, blank=True, folder='Certificates'
    )
    name = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user_type != 'professional':
            raise ValueError("Only professionals can create certificates.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or 'Unnamed Certificate'

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-created_at']


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
    ]
    
    MONTHLY_COSTS = {
        'silver': Decimal('100.00'),
        'gold': Decimal('200.00'),
        'diamond': Decimal('300.00'),
    }
    
    
    REQUEST_COINS = {
        'silver': 100,   
        'gold': 300,    
        'diamond': 500,
    }


    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '1 Year'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if self.plan_type in self.MONTHLY_COSTS and self.duration:
            monthly_cost = self.MONTHLY_COSTS[self.plan_type]
            self.cost = monthly_cost * self.duration
            self.end_date = self.start_date + timedelta(days=self.duration * 30)
        else:
            raise ValueError("Missing plan_type or duration for cost calculation.")
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.end_date if self.end_date else False

    def __str__(self):
        return f"{self.professional} - {self.plan_type} - {self.duration} Plan"

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('transaction', 'Transaction'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments',null=True)  # The customer making the payment
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payments')  # Professional receiving the payment
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)  # Nullable for subscriptions
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False) 
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES,null=True)  # To differentiate between subscription and transaction
    payment_method = models.CharField(max_length=50, default='chapa', null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment {self.transaction_id} from {self.user.email} to {self.professional.email} - Amount: {self.amount}"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        
        
class VerificationRequest(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.OneToOneField(User, on_delete=models.CASCADE,default=None, related_name='verification_requests')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
         unique_together = ('professional', 'status')
         
         
    def save(self, *args, **kwargs):
        if self.status in ['approved', 'rejected'] and not self.verified_by:
            raise ValueError("An admin must verify the request before approving or rejecting.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification Request for {self.professional} staus {self.status}"
    
