from rest_framework import serializers
from django.utils import timezone
from .models import  ServicePost, ServicePostApplication, ServiceBooking
from common.models import Category
from common.serializers import UserSerializer,CategorySerializer
from users.serializers import CustomerSerializer,ProfessionalSerializer
            
class ServicePostSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = ServicePost
        fields = [
            "id", "customer", "category", "description", 
            "status", "urgency", "work_due_date", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at","customer"]

    def validate_work_due_date(self, value):
        """Validate that the work due date is not in the past."""
        if value and value < timezone.now():
            raise serializers.ValidationError("The work due date cannot be in the past.")
        return value  
        

class ServicePostApplicationSerializer(serializers.ModelSerializer):
    service = ServicePostSerializer(read_only=False)
    professional = ProfessionalSerializer(read_only=False)
    class Meta:
        model = ServicePostApplication
        fields = ['id', 'service', 'professional', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Prevent duplicate applications
        service = validated_data['service']
        professional = validated_data['professional']
        if ServicePostApplication.objects.filter(service=service, professional=professional).exists():
            raise serializers.ValidationError("You have already applied for this service.")
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'status' in validated_data:
            raise serializers.ValidationError("You cannot change the application status.")
        return super().update(instance, validated_data)
    
    


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