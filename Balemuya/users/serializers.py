from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import User, Address, Permission, Admin, AdminLog, Customer, Skill, Professional, Education, Portfolio, Certificate,\
    Payment, SubscriptionPlan, VerificationRequest, Notification
from common.models import Category
from common.serializers import CategorySerializer,UserSerializer


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



class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


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
        fields = ['id','school', 'degree', 'field_of_study', 'created_at', 'updated_at']
        read_only_fields = ['id','created_at', 'updated_at']
        write_only_fields = ['professional']
    
    def create(self, validated_data):
        return Education.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)



class PortfolioSerializer(serializers.ModelSerializer):
    portfolio_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'image', 'portfolio_image_url','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['professional']
     
    def get_portfolio_image_url(self,obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    def create(self, validated_data):
       return Portfolio.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)
    
   

class CertificateSerializer(serializers.ModelSerializer):
    certificate_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'image', 'name', 'certificate_image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['professional']

    def get_certificate_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def create(self, validated_data):
        return Certificate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['professional'] = instance.professional
        return super().update(instance, validated_data)



class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)  # Allow user to be set during creation
    kebele_id_front_image_url = serializers.SerializerMethodField()
    kebele_id_back_image_url = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True,read_only=True)
    skills = SkillSerializer(many=True,read_only=True)
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