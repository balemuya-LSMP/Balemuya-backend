from rest_framework import serializers
from django.utils import timezone
from .models import  ServicePost, ServicePostApplication, ServiceBooking,Review,Complain
from users.models import Customer, Professional
from common.models import Category
from common.serializers import UserSerializer,CategorySerializer
from users.serializers import CustomerSerializer,ProfessionalSerializer
from common.serializers import AddressSerializer


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'booking', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at','booking']
        
    def create(self, validated_data):
        user = validated_data.pop('user', self.context['request'].user)
        
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
        
class ComplainSerializer(serializers.ModelSerializer):
    
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
    customer_id = serializers.UUIDField(source='customer.id',read_only=True)
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    customer_rating = serializers.DecimalField(source='customer.rating', read_only=True, max_digits=3, decimal_places=2)
    customer_service_booked_count = serializers.IntegerField(source='customer.service_booked', read_only=True)
    customer_profile_image = serializers.ImageField(source='customer.user.profile_image', read_only=True)
    category =  serializers.CharField(source='category.name')
    location = AddressSerializer(required=False)

    class Meta:
        model = ServicePost
        fields = [
            "id","title", "category", "description", "location",
            "status", "urgency", "work_due_date", "created_at", "updated_at",'customer_id',
            "customer_name", "customer_rating", "customer_service_booked_count", "customer_profile_image"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        

    def validate_work_due_date(self, value):
        """Validate that the work due date is not in the past."""
        if value and value < timezone.now():
            raise serializers.ValidationError("The work due date cannot be in the past.")
        return value 

    def create(self, validated_data):
        user = self.context['request'].user
        category = self.get_or_create_category(validated_data.pop('category', None))

        location_data = validated_data.pop('location', None)

        if location_data:
            location = self.create_location(location_data)
        else:
            location = self.get_default_address(user)

        validated_data['category'] = category
        validated_data['location'] = location
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        category = self.get_or_create_category(validated_data.pop('category', None))
        if location_data:
            location = self.create_location(location_data)
        else:
            location = self.get_default_address(instance.customer.user)
        
        validated_data['location'] = location
        validated_data['category'] = category
        return super().update(instance, validated_data)

    def get_or_create_category(self, category_name):
        """Get or create a category instance."""
        if not category_name:
            raise serializers.ValidationError("Category data must be provided with a name.")

        category, created = Category.objects.get_or_create(name=category_name)

        if created:
            print(f"Created new category: {category_name}")
        else:
            print(f"Using existing category: {category_name}")

        return category

    def create_location(self, location_data):
        """Create and validate an address instance."""
        location_serializer = AddressSerializer(data=location_data)
        if location_serializer.is_valid():
            address_instance = location_serializer.save() 
            return address_instance
        else:
            raise serializers.ValidationError(location_serializer.errors)

    def get_default_address(self, user):
        """Retrieve the default address for the user."""
        default_address = user.address
        if not default_address:
            raise serializers.ValidationError("User does not have a default address.")
        return default_address
    


class ServicePostApplicationSerializer(serializers.ModelSerializer):
    professional_id = serializers.UUIDField(source='professional.id',read_only=True)
    service = ServicePostSerializer(read_only=True)
    professional_name = serializers.CharField(source='professional.user.get_full_name', read_only=True)
    professional_profile_image = serializers.ImageField(source='professional.user.profile_image', read_only=True)
    rating = serializers.FloatField(source='professional.rating', read_only=True)
    
    
    class Meta:
        model = ServicePostApplication
        fields = ['id','service','professional_id','professional','professional_name', 'professional_profile_image', 'rating', 'professional_id', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['professional']

    def validate(self, attrs):
        # Set professional_id from context if not provided
        if 'professional' not in attrs:
            professional = self.context['request'].user.professional
            if professional is None:
                raise serializers.ValidationError("Professional not found for the user.")
            attrs['professional'] = professional  # Set the professional ID
        return attrs

    def create(self, validated_data):
        service = validated_data.get('service_id')  
        professional = self.context['request'].user.professional
        
        if ServicePostApplication.objects.filter(service=service, professional=professional).exists():
            raise serializers.ValidationError("You have already applied for this service.")

        return super().create(validated_data)

class ServiceBookingSerializer(serializers.ModelSerializer):
    application = ServicePostApplicationSerializer(read_only=True)
    class Meta:
        model = ServiceBooking
        fields = ['id', 'application', 'scheduled_date', 'agreed_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        application = data.get('application')

        # Check if the application status is "accepted"
        if application.status != 'accepted':
            raise serializers.ValidationError("The application must be accepted before creating a booking.")

        if ServiceBooking.objects.filter(application=application).exists():
            raise serializers.ValidationError("A booking already exists for this application.")

        agreed_price = data.get('agreed_price')
        if agreed_price is None or agreed_price <= 0:
            raise serializers.ValidationError("The agreed price must be a positive value.")

        return data