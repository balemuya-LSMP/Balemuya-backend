from rest_framework import serializers
from django.utils import timezone
from .models import ServicePost, ServicePostApplication, ServiceBooking, Review, Complain
from users.models import Customer, Professional
from common.models import Category
from common.serializers import UserSerializer, CategorySerializer
from users.serializers import CustomerSerializer, ProfessionalSerializer
from common.serializers import AddressSerializer
from uuid import UUID

class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'booking', 'reviewer', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']
        write_only_fields = ['user']

    def create(self, validated_data):
        user = validated_data.pop('user', None)  
        booking = validated_data.pop('booking', None)

        review = Review.objects.create(user=user, booking=booking, **validated_data)
        return review

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
class ComplainSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    complaint = UserSerializer(read_only=True)

    class Meta:
        model = Complain
        fields = ['id', 'complaint','user','booking', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['user','booking']

    def create(self, validated_data):
        user=validated_data.pop('user',None)
        booking = validated_data.pop('booking',None)
        
        complain = Complain.objects.create(booking=booking,user=user,**validated_data)
        return complain

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ServicePostSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    category = serializers.CharField()
    location = AddressSerializer(required=False)
    customer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ServicePost
        fields = [
            "id",'customer_id',"title", "category", "customer", "description", "location",
            "status", "urgency", "work_due_date", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_work_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("The work due date cannot be in the past.")
        return value

    def create(self, validated_data):
        request=self.context.get('request')
        user = request.user
        category_name = validated_data.pop('category', None)
        category = self.get_or_create_category(category_name)

        location_data = validated_data.pop('location', None)
        location = self.create_or_get_location(user, location_data)
        
        validated_data['category'] = category
        validated_data['location'] = location

        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        category = self.get_or_create_category(category_name)

        location_data = validated_data.pop('location', None)
        location = self.create_or_get_location(instance.customer.user, location_data)

        validated_data['category'] = category
        validated_data['location'] = location
        return super().update(instance, validated_data)

    def get_or_create_category(self, category_name):
        if not category_name:
            raise serializers.ValidationError("Category name must be provided.")
        category, created = Category.objects.get_or_create(name=category_name)
        return category

    def create_or_get_location(self, user, location_data):
        if location_data:
            location_serializer = AddressSerializer(data=location_data)
            if location_serializer.is_valid():
                return location_serializer.save()
            raise serializers.ValidationError(location_serializer.errors)
        return self.get_default_address(user)

    def get_default_address(self, user):
        if not hasattr(user, 'address') or not user.address:
            raise serializers.ValidationError("User does not have a default address.")
        return user.address

class ServicePostApplicationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service_id = serializers.UUIDField(write_only=True)
    professional_id = serializers.UUIDField(write_only=True)
    service = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField() 
    customer = serializers.SerializerMethodField()
    

    class Meta:
        model = ServicePostApplication
        fields = ['id', 'service_id','professional_id','service', 'professional', 'customer', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_service(self, obj):
        service_data = ServicePostSerializer(obj.service).data
        service_data.pop('customer', None)  
        return service_data

    def get_professional(self, obj):
        return {
            "professional_id": str(obj.professional.id),
            "professional_name": obj.professional.user.get_full_name(),
            "professional_profile_image": obj.professional.user.profile_image.url if obj.professional.user.profile_image else None,
            "rating": obj.professional.rating
        }

    def get_customer(self, obj):
        if obj.service and obj.service.customer:
            customer = obj.service.customer
            return {
                "customer_id": str(customer.user.id),
                "customer_name": customer.user.get_full_name(),
                "customer_profile_image": customer.user.profile_image.url if customer.user.profile_image else None,
                "customer_rating": customer.rating,
            }
        return None

    def create(self, validated_data):
        professional_id=validated_data['professional_id'] 
        service_id=validated_data['service_id'] 
        validated_data['status'] = 'pending'

        if ServicePostApplication.objects.filter(service=service_id, professional=professional_id).exists():
            raise serializers.ValidationError("You have already applied for this service.")

        return super().create(validated_data)

class ServiceBookingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    service = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField() 
    professional = serializers.SerializerMethodField() 

    class Meta:
        model = ServiceBooking
        fields = ['id', 'application','service','professional','customer' ,'scheduled_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields=['application']

    def get_service(self, obj):
        service_data = ServicePostSerializer(obj.application.service).data
        service_data.pop('customer', None)
        return service_data

    def get_professional(self, obj):
        return {
            "professional_id": str(obj.application.professional.id),
            "professional_name": obj.application.professional.user.get_full_name(),
            "professional_profile_image": obj.application.professional.user.profile_image.url if obj.application.professional.user.profile_image else None,
            "rating": obj.application.professional.rating
        }

    def get_customer(self, obj):
        return {
            "customer_id": str(obj.application.service.customer.user.id),
            "customer_name": obj.application.service.customer.user.get_full_name(),
            "customer_profile_image": obj.application.service.customer.user.profile_image.url if obj.application.service.customer.user.profile_image else None,
            "customer_rating": obj.application.service.customer.rating,
        }

    def validate(self, data):
        application = data.get('application')

        if application and application.status != 'accepted':
            raise serializers.ValidationError("The application must be accepted before creating a booking.")

        if ServiceBooking.objects.filter(application=application).exists():
            raise serializers.ValidationError("A booking already exists for this application.")

        return data