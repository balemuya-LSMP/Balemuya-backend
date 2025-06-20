
from rest_framework import serializers
from rest_framework import exceptions
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
import re

from services.models import Category    
from users.models import User, Address,Professional,Customer,Admin


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Category
        fields = ['id','name']
        
 
 
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'region', 'city', 'latitude', 'longitude']
        
        


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    email = serializers.EmailField(max_length=200)
    profile_image_url = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'id', 'password','full_name', 'profile_image','profile_image_url','email','username', 'gender', 'org_name', 'first_name', 'last_name','phone_number', 'user_type','entity_type', 'bio',
            'is_active','telegram_chat_id','is_blocked','created_at', 'updated_at', 'address'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None
    
    def get_full_name(self, obj):
        if obj.user_type == 'professional':
            if obj.entity_type == 'organization':
                return obj.org_name
            elif obj.entity_type == 'individual':
                return f"{obj.first_name} {obj.last_name}"
        elif obj.user_type == 'customer':
            if obj.entity_type == 'organization':
                return obj.org_name
            elif obj.entity_type == 'individual':
                return f"{obj.first_name} {obj.last_name}"
        elif obj.user_type == 'admin':
            return obj.first_name
        return None

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")

        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")

        user_id = getattr(self.instance, 'id', None) 
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Email already exists.")
        
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate_phone_number(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Phone number must be in a valid format.")
        return value
    
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user_type = instance.user_type
        entity_type = instance.entity_type

        if entity_type == 'organization':
            rep.pop('first_name', None)
            rep.pop('last_name', None)
            rep.pop('gender', None)

        elif entity_type == 'individual':
            rep.pop('org_name', None)
        
        elif entity_type =='admin':
            rep.pop('org_name',None)
               
        return rep
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise ValidationError("Password is required.")
        self.validate_password(password)

        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()

            if user.user_type == 'professional':
                Professional.objects.create(user=user)
           
            elif user.user_type == 'customer':
                Customer.objects.create(user=user)
            
            elif user.user_type == 'admin':
                Admin.objects.create(user=user)

            return user

    def update(self, instance, validated_data):
        email = validated_data.get('email', instance.email)
        validated_data['email'] = self.validate_email(email)  

        # Update instance attributes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
