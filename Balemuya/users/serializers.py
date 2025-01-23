from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import User, Address, Permission, Admin, AdminLog, Customer, Skill, Professional, Education, Portfolio, Certificate,\
    Payment, SubscriptionPlan, VerificationRequest, Notification
from services.models import Category
from services.serializers import CategorySerializer  # Import the existing CategorySerializer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'region', 'city', 'latitude', 'longitude', 'is_current']



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient','sender', 'message', 'is_read', 'created_at']
        

class VerificationRequestSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.user.username', read_only=True)

    class Meta:
        model = VerificationRequest
        fields = ['id', 'professional', 'professional_name', 'status', 'admin_comment', 'created_at', 'updated_at']
        read_only_fields = ['status', 'admin_comment', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    email = serializers.EmailField(max_length=200)
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'profile_image','profile_image_url','gender', 
                  'email', 'phone_number', 'user_type', 'is_active', 'is_blocked', 
                  'created_at', 'updated_at', 'addresses']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
    def get_profile_image_url(self,obj):
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None

    def validate_email(self, value):
        # Custom email validation logic
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_phone_number(self, value):
        # Custom phone number validation logic
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Phone number must be in a valid format.")
        return value

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if user.user_type == 'professional':
            Professional.objects.create(user=user)
        elif user.user_type == 'customer':
            Customer.objects.create(user=user)
        elif user.user_type == 'admin':
            Admin.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if instance.email != email:
            instance.email = email
            
        instance.save()

        return instance

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    permissions = PermissionSerializer(many=True, required=False)

    class Meta:
        model = Admin
        fields = ['user','permissions']
        


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update main profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Handle permissions update
        self._update_permissions(instance, validated_data)

        return instance

    def _update_permissions(self, instance, validated_data):
        if 'permissions' in validated_data:
            instance.permissions.clear()

            # Add new permissions
            for permission_data in validated_data['permissions']:
                permission_serializer = PermissionSerializer(data=permission_data)
                permission_serializer.is_valid(raise_exception=True)
                permission_serializer.save()  # Save the permission instance
                instance.permissions.add(permission_serializer.instance)


class AdminLogSerializer(serializers.ModelSerializer):
    admin = AdminSerializer()

    class Meta:
        model = AdminLog
        fields = ['admin', 'action', 'timestamp']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Customer
        fields =['user', 'rating']
        

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        with transaction.atomic():
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            customer = Customer.objects.create(user=user, **validated_data)
            return customer
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'professional', 'school', 'degree', 'field_of_study', 'created_at', 'updated_at']
        read_only_fields = ['id', 'professional', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['professional'] = self.context['request'].user.professional
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)



class PortfolioSerializer(serializers.ModelSerializer):
    portfolio_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Portfolio
        fields = ['id', 'professional', 'title', 'description', 'image', 'portfolio_image_url','created_at', 'updated_at']
        read_only_fields = ['id', 'professional', 'created_at', 'updated_at']
     
    def get_portfolio_image_url(self,obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    def create(self, validated_data):
        validated_data['professional'] = self.context['request'].user.professional
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)
    
   

class CertificateSerializer(serializers.ModelSerializer):
    certificate_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'professional', 'image', 'name', 'certificate_image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'professional', 'created_at', 'updated_at']

    def get_certificate_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def create(self, validated_data):
        validated_data['professional'] = self.context['request'].user.professional
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)



class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)  # Allow user to be set during creation
    kebele_id_front_image_url = serializers.SerializerMethodField()
    kebele_id_back_image_url = serializers.SerializerMethodField()
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, required=False)
    educations = EducationSerializer(many=True, read_only=True)  
    portfolios = PortfolioSerializer(many=True, read_only=True) 
    certificates = CertificateSerializer(many=True, read_only=True) 

    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'kebele_id_front_image', 
            'kebele_id_front_image_url', 'kebele_id_back_image', 'kebele_id_back_image_url',
            'categories', 'skills', 'rating', 'years_of_experience', 'is_available', 
            'is_verified', 'bio', 'balance', 'educations', 'portfolios', 'certificates'
        ]
        read_only_fields = ['id', 'kebele_id_front_image_url', 'kebele_id_back_image_url', 'educations', 'portfolios', 'certificates', 'addresses']


    def get_kebele_id_front_image_url(self, obj):
        if obj.kebele_id_front_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.kebele_id_front_image.url) if request else obj.kebele_id_front_image.url
        return None

    def get_kebele_id_back_image_url(self, obj):
        if obj.kebele_id_back_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.kebele_id_back_image.url) if request else obj.kebele_id_back_image.url
        return None

    def create(self, validated_data):
        # Automatically associate the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user  # Associate the professional with the current user
        return super().create(validated_data)