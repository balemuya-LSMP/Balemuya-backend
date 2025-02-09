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
    class Meta:
        model = Review
        fields = ['id', 'user', 'booking', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'booking']

    def create(self, validated_data):
        user = validated_data.pop('user', self.context['request'].user)
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ComplainSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = Complain
        fields = ['id', 'customer', 'professional', 'complain', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['customer'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ServicePostSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(source='customer.user.id', read_only=True)
    customer_rating = serializers.DecimalField(source='customer.rating', read_only=True, max_digits=3, decimal_places=2)
    customer_service_booked_count = serializers.IntegerField(source='customer.service_booked', read_only=True)
    customer_first_name = serializers.CharField(source='customer.user.first_name', read_only=True)
    customer_middle_name = serializers.CharField(source='customer.user.middle_name', read_only=True)
    customer_profile_image = serializers.ImageField(source='customer.user.profile_image', read_only=True)

    category = serializers.CharField()
    location = AddressSerializer(required=False)

    class Meta:
        model = ServicePost
        fields = [
            "id", "title", "category", "description", "location",
            "status", "urgency", "work_due_date", "created_at", "updated_at", "customer_id",
            "customer_first_name","customer_middle_name", "customer_rating", "customer_service_booked_count", "customer_profile_image"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_work_due_date(self, value):
        """Validate that the work due date is not in the past."""
        if value and value < timezone.now():
            raise serializers.ValidationError("The work due date cannot be in the past.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
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
        """Get or create a category instance."""
        if not category_name:
            raise serializers.ValidationError("Category name must be provided.")
        category, created = Category.objects.get_or_create(name=category_name)
        return category

    def create_or_get_location(self, user, location_data):
        """Handles location creation or retrieving the default address."""
        if location_data:
            location_serializer = AddressSerializer(data=location_data)
            if location_serializer.is_valid():
                return location_serializer.save()
            raise serializers.ValidationError(location_serializer.errors)
        return self.get_default_address(user)

    def get_default_address(self, user):
        """Retrieve the default address for the user."""
        if not hasattr(user, 'address') or not user.address:
            raise serializers.ValidationError("User does not have a default address.")
        return user.address

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['customer_id'] = str(representation['customer_id'])  # Convert UUID to string
        return representation

class ServicePostApplicationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    professional_id = serializers.CharField(source='professional.id', read_only=True)
    professional_name = serializers.CharField(source='professional.user.get_full_name', read_only=True)
    professional_profile_image = serializers.ImageField(source='professional.user.profile_image', read_only=True)
    rating = serializers.FloatField(source='professional.rating', read_only=True)
    professional = serializers.PrimaryKeyRelatedField(queryset = Professional.objects.all(),write_only=True,required=False)
    service = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ServicePostApplication
        fields = ['id', 'service', 'professional_id', 'professional', 'professional_name', 'professional_profile_image', 'rating', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['professional']


    def create(self, validated_data):
        service = validated_data.get('service')
        request = self.context.get('request')
        service = self.context.get('service')
        
        professional =request.user.professional      
        validated_data['professional'] = professional        
        validated_data['service'] = service        
        validated_data['status'] = 'pending'
        
        if ServicePostApplication.objects.filter(service=service, professional=professional).exists():
            raise serializers.ValidationError("You have already applied for this service.")

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['professional_id'] = str(representation['professional_id']) 
        return representation

class ServiceBookingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = ServiceBooking
        fields = ['id', 'application', 'scheduled_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        application = data.get('application')

        # Check if the application status is "accepted"
        if application and application.status != 'accepted':
            raise serializers.ValidationError("The application must be accepted before creating a booking.")

        if ServiceBooking.objects.filter(application=application).exists():
            raise serializers.ValidationError("A booking already exists for this application.")

        return data