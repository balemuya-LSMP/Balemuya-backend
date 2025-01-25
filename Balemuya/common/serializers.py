
from rest_framework import serializers
from rest_framework import exceptions
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

from services.models import Category    
from users.models import User, Address


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Category
        fields = ['name']
        
 
 
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'region', 'city', 'latitude', 'longitude', 'is_current']


        
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
