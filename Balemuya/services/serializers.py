from rest_framework import serializers
from django.utils import timezone
from .models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain,ServiceRequest,ServicePostReport
from users.models import Customer, Professional
from common.models import Category
from common.serializers import UserSerializer, CategorySerializer
from users.serializers import CustomerSerializer, ProfessionalSerializer
from common.serializers import AddressSerializer
from uuid import UUID

# ---------- Review Serializer ----------
class ReviewSerializer(serializers.ModelSerializer):
    # id = serializers.CharField(read_only=True)
    # reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'booking', 'service_request', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']
        extra_kwargs = {'user': {'write_only': True}}

    def create(self, validated_data):
        if not validated_data.get('booking') and not validated_data.get('service_request'):
            raise serializers.ValidationError("A review must be linked to a booking or a service request.")
        return Review.objects.create(**validated_data)
    
class ReviewDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'user', 'booking', 'service_request', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'user': {'write_only': True}}

    

# ---------- Complain Serializer ----------
class ComplainSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Complain
        fields = ['id','user', 'booking', 'service_request', 'status', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'user': {'write_only': True}}

    def create(self, validated_data):
        if not validated_data.get('booking') and not validated_data.get('service_request'):
            raise serializers.ValidationError("A complaint must be linked to a booking or a service request.")
        return Complain.objects.create(**validated_data)
    
class ComplainDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Complain
        fields = ['id','user', 'booking', 'service_request', 'status', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'user': {'write_only': True}}


# ---------- Service Post Serializer ----------
class ServicePostSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    location = AddressSerializer(required=False)
    class Meta:
        model = ServicePost
        fields = ["id", "title", "category", "customer", "description", "location", "status", "urgency", "work_due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_work_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Work due date cannot be in the past.")
        return value

    def create(self, validated_data):
        validated_data['category'] = self.get_or_create_category(validated_data.pop('category'))
        validated_data['location'] = self.create_or_get_location(validated_data.pop('location', None))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['category'] = self.get_or_create_category(validated_data.pop('category'))
        validated_data['location'] = self.create_or_get_location(validated_data.pop('location', None))
        return super().update(instance, validated_data)

    def get_or_create_category(self, name):
        if not name:
            raise serializers.ValidationError("Category is required.")
        return Category.objects.get_or_create(name=name)[0]

    def create_or_get_location(self, data):
        if data:
            serializer = AddressSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.save()
        user = self.context.get('request').user
        if not hasattr(user, 'address') or not user.address:
            raise serializers.ValidationError("User has no default address.")
        return user.address
    
# ---------- Service Post detail Serializer ----------
class ServicePostDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    category = serializers.CharField()
    location = AddressSerializer(required=False)
    class Meta:
        model = ServicePost
        fields = ["id", "title", "category", "customer", "description", "location", "status", "urgency", "work_due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------- Service Post Application Serializer ----------
class ServicePostApplicationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service_id = serializers.UUIDField(write_only=True)
    professional_id = serializers.UUIDField(write_only=True)
    service = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = ServicePostApplication
        fields = ['id', 'service_id', 'professional_id', 'service', 'professional', 'customer', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_service(self, obj):
        data = ServicePostSerializer(obj.service).data
        data.pop('customer', None)
        return data

    def get_professional(self, obj):
        p = obj.professional
        return {
            "professional_id": str(p.id),
            "professional_name": p.user.username,
            "professional_profile_image": p.user.profile_image.url if p.user.profile_image else None,
            "rating": p.rating
        }

    def get_customer(self, obj):
        c = obj.service.customer if obj.service else None
        if not c: return None
        return {
            "customer_id": str(c.user.id),
            "customer_name": c.user.username,
            "customer_profile_image": c.user.profile_image.url if c.user.profile_image else None,
            "customer_rating": c.rating
        }

    def create(self, validated_data):
        if ServicePostApplication.objects.filter(
            service=validated_data['service_id'], professional=validated_data['professional_id']
        ).exists():
            raise serializers.ValidationError("Already applied for this service.")
        validated_data['status'] = 'pending'
        return super().create(validated_data)

# ---------- Service Booking Serializer ----------
class ServiceBookingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()

    class Meta:
        model = ServiceBooking
        fields = ['id', 'application', 'service', 'professional', 'customer', 'scheduled_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'service', 'professional']
        extra_kwargs = {'application': {'write_only': True}}

    def get_service(self, obj):
        try:
            data = ServicePostSerializer(obj.application.service).data
            data.pop('customer', None)
            return data
        except: return None

    def get_professional(self, obj):
        try:
            p = obj.application.professional
            return {
                "professional_id": str(p.id),
                "professional_name": p.user.get_full_name(),
                "professional_profile_image": p.user.profile_image.url if p.user.profile_image else None,
                "rating": p.rating,
                "phone_number": p.user.phone_number
            }
        except: return None

    def get_customer(self, obj):
        try:
            c = obj.application.service.customer
            return {
                "customer_id": str(c.user.id),
                "customer_name": c.user.username,
                "customer_profile_image": c.user.profile_image.url if c.user.profile_image else None,
                "customer_rating": c.rating
            }
        except: return None

    def validate(self, data):
        app = data.get('application')
        if app.status != 'accepted':
            raise serializers.ValidationError("Application must be accepted before booking.")
        if ServiceBooking.objects.filter(application=app).exists():
            raise serializers.ValidationError("Booking already exists for this application.")
        return data

# ---------- Service Request Serializer ----------
class ServiceRequestSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    professional = serializers.SerializerMethodField()
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer', write_only=True)
    professional_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='professional', write_only=True)

    class Meta:
        model = ServiceRequest
        fields = ['id', 'customer', 'customer_id', 'professional', 'professional_id', 'detail', 'status', 'created_at', 'updated_at']

    def get_professional(self, obj):
        try:
            p = obj.professional
            return {
                "professional_id": str(p.id),
                "professional_name": p.user.get_full_name(),
                "professional_profile_image": p.user.profile_image.url if p.user.profile_image else None,
                "rating": p.rating
            }
        except: return None

    def create(self, validated_data):
        return ServiceRequest.objects.create(**validated_data)
    
    

class ServicePostReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    service_post = ServicePostSerializer(read_only=True)
    class Meta:
        model = ServicePostReport
        fields = ['id', 'service_post', 'reporter', 'reason', 'created_at','updated_at']
        read_only_fields = ['id', 'created_at','updated_at', 'reporter']
