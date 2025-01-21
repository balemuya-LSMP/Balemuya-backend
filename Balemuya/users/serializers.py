from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import User, Address, Permission, Admin, AdminLog, Customer, Skill, Professional, Education, Portfolio, Certificate
from services.models import Category
from services.serializers import CategorySerializer  # Import the existing CategorySerializer


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'gender',
                  'email', 'password', 'phone_number', 'user_type',
                  'is_active', 'is_blocked', 'created_at', 'addresses']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(_("Invalid email format."))

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this Email already exists.")
        return value

    def validate_phone_number(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(_("Phone number must be in a valid format."))
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(_("Password must be at least 8 characters long."))
        return value

    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', [])
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # Create or reuse addresses
        for address_data in addresses_data:
            address = Address.objects.create(user=user, **address_data)

            if address_data.get('is_current'):
                Address.objects.filter(user=user, is_current=True).update(is_current=False)
                address.is_current = True
                address.save()

        if user.user_type == 'professional':
            Professional.objects.create(user=user)

        if user.user_type == 'customer':
            Customer.objects.create(user=user)

        if user.user_type == 'admin':
            Admin.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        addresses_data = validated_data.pop('addresses', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update addresses if provided
        if addresses_data is not None:
            for address_data in addresses_data:
                address, created = Address.objects.get_or_create(user=instance, **address_data)

                if address_data.get('is_current'):
                    Address.objects.filter(user=instance, is_current=True).update(is_current=False)
                    address.is_current = True
                    address.save()

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
    profile_image_url =serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = ['user','permissions', 'profile_image', 'profile_image_url']
        
    
    def get_profile_image_url(self,obj):
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None


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
            # Clear existing permissions
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
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields =['user', 'rating', 'profile_image', 'profile_image_url']
        
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None
    

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
        fields = [
            'id', 'school', 'degree', 'field_of_study', 
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        return Education.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class PortfolioSerializer(serializers.ModelSerializer):
    portfolio_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'description', 'image','portfolio_image_url',
            'created_at', 'updated_at'
        ]
    
    
    def get_portfolio_image_url(self,obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    
    def create(self, validated_data):
        return Portfolio.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CertificateSerializer(serializers.ModelSerializer):
    certificate_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Certificate
        fields = [
            'id', 'professional', 'image', 'name','certificate_image_url',
            'created_at', 'updated_at'
        ]
    
    def get_certificate_image_url(self,obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    
    def create(self, validated_data):
        return Certificate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    skills = SkillSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)  # Ensure these serializers are defined
    portfolios = PortfolioSerializer(many=True, required=False)
    certificates = CertificateSerializer(many=True, required=False)
    categories = CategorySerializer(many=True, required=False)
    profile_image_url = serializers.SerializerMethodField()
    kebele_id_front_image_url = serializers.SerializerMethodField()
    kebele_id_back_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = '__all__'
        
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_image.url) if request else obj.profile_image.url
        return None
    
    def get_kebele_id_front_image_url(self, obj):
        if obj.kebele_id_front_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.kebele_id_front_image.url) if request else obj.kebele_id_front_image.url
        return None
    
    def get_kebele_id_back_image_url(self, obj):
        if obj.kebele_id_back_image:  # Change from self.kebele_id_back_image to obj.kebele_id_back_image
            request = self.context.get('request')
            return request.build_absolute_uri(obj.kebele_id_back_image.url) if request else obj.kebele_id_back_image.url
        return None
        

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        skills_data = validated_data.pop('skills', [])
        educations_data = validated_data.pop('educations', [])
        portfolios_data = validated_data.pop('portfolios', [])
        certificates_data = validated_data.pop('certificates', [])
        categories_data = validated_data.pop('categories', [])  # Extract categories data

        with transaction.atomic():
            user = self._handle_user_creation(user_data)
            professional = Professional.objects.create(user=user, **validated_data)

            # Handle nested creations
            self._handle_nested_creations(professional, skills_data, educations_data, portfolios_data, certificates_data, categories_data)

        return professional

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        skills_data = validated_data.pop('skills', None)
        educations_data = validated_data.pop('educations', None)
        portfolios_data = validated_data.pop('portfolios', None)
        certificates_data = validated_data.pop('certificates', None)
        categories_data = validated_data.pop('categories', None)  # Extract categories data

        # Update user if provided
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Handle nested updates
        if skills_data is not None:
            self._handle_nested_updates(instance, skills_data, 'skills')

        if educations_data is not None:
            self._handle_nested_updates(instance, educations_data, 'educations')

        if portfolios_data is not None:
            self._handle_nested_updates(instance, portfolios_data, 'portfolios')

        if certificates_data is not None:
            self._handle_nested_updates(instance, certificates_data, 'certificates')

        if categories_data is not None:
            self._handle_nested_updates(instance, categories_data, 'categories')  # Handle categories update

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _handle_user_creation(self, user_data):
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        return user_serializer.save()

    def _handle_nested_creations(self, profile, skills_data, educations_data, portfolios_data, certificates_data, categories_data):
        # Create skills
        for skill_data in skills_data:
            skill_id = skill_data.get('id')
            if skill_id:
                skill = Skill.objects.filter(id=skill_id).first()
                if skill:
                    profile.skills.add(skill)
            else:
                skill_serializer = SkillSerializer(data=skill_data)
                skill_serializer.is_valid(raise_exception=True)
                skill = skill_serializer.save()
                profile.skills.add(skill)

        # Create educations
        for education_data in educations_data:
            education_serializer = EducationSerializer(data=education_data)
            education_serializer.is_valid(raise_exception=True)
            education_serializer.save(professional=profile)

        # Create portfolios
        for portfolio_data in portfolios_data:
            portfolio_serializer = PortfolioSerializer(data=portfolio_data)
            portfolio_serializer.is_valid(raise_exception=True)
            portfolio_serializer.save(professional=profile)

        # Create certificates
        for certificate_data in certificates_data:
            certificate_serializer = CertificateSerializer(data=certificate_data)
            certificate_serializer.is_valid(raise_exception=True)
            certificate_serializer.save(professional=profile)

        # Create categories
        for category_data in categories_data:
            category_id = category_data.get('id')
            if category_id:
                category = Category.objects.filter(id=category_id).first()
                if category:
                    profile.categories.add(category)

    def _handle_nested_updates(self, profile, data, field_name):
        # Update based on provided data
        for item_data in data:
            if field_name == 'skills':
                skill_id = item_data.get('id')
                if skill_id:
                    skill = Skill.objects.filter(id=skill_id).first()
                    if skill:
                        profile.skills.add(skill)
                else:
                    skill_serializer = SkillSerializer(data=item_data)
                    skill_serializer.is_valid(raise_exception=True)
                    skill = skill_serializer.save()
                    profile.skills.add(skill)

            elif field_name == 'educations':
                education_id = item_data.get('id')
                if education_id:
                    education_instance = Education.objects.filter(id=education_id, professional=profile).first()
                    if education_instance:
                        education_serializer = EducationSerializer(instance=education_instance, data=item_data, partial=True)
                        education_serializer.is_valid(raise_exception=True)
                        education_serializer.save()
                else:
                    education_serializer = EducationSerializer(data=item_data)
                    education_serializer.is_valid(raise_exception=True)
                    education_serializer.save(professional=profile)

            elif field_name == 'portfolios':
                portfolio_id = item_data.get('id')
                if portfolio_id:
                    portfolio_instance = Portfolio.objects.filter(id=portfolio_id, professional=profile).first()
                    if portfolio_instance:
                        portfolio_serializer = PortfolioSerializer(instance=portfolio_instance, data=item_data, partial=True)
                        portfolio_serializer.is_valid(raise_exception=True)
                        portfolio_serializer.save()
                else:
                    portfolio_serializer = PortfolioSerializer(data=item_data)
                    portfolio_serializer.is_valid(raise_exception=True)
                    portfolio_serializer.save(professional=profile)

            elif field_name == 'certificates':
                certificate_id = item_data.get('id')
                if certificate_id:
                    certificate_instance = Certificate.objects.filter(id=certificate_id, professional=profile).first()
                    if certificate_instance:
                        certificate_serializer = CertificateSerializer(instance=certificate_instance, data=item_data, partial=True)
                        certificate_serializer.is_valid(raise_exception=True)
                        certificate_serializer.save()
                else:
                    certificate_serializer = CertificateSerializer(data=item_data)
                    certificate_serializer.is_valid(raise_exception=True)
                    certificate_serializer.save(professional=profile)

            elif field_name == 'categories':
                category_id = item_data.get('id')
                if category_id:
                    category = Category.objects.filter(id=category_id).first()
                    if category:
                        profile.categories.add(category)