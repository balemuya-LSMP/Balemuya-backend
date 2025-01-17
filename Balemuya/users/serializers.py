from rest_framework import serializers
import re
import dns.resolver
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import User, Address, Permission, AdminProfile, AdminLog, CustomerProfile, Skill, ProfessionalProfile, Education, Portfolio, Certificate

from services.serializers import CategorySerializer
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
            'password':{'write_only':True}  
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

        # domain = value.split('@')[-1]
        # try:
        #     dns.resolver.resolve(domain, 'MX')
        # except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        #     raise serializers.ValidationError(_("Email domain does not exist."))

 
        if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this Email already exists.")
        return value

    def validate_phone_number(self,value):
            
            if not re.match(r'^\+?1?\d{9,15}$', value):
                  raise serializers.ValidationError(_("Phone number must be in a valid format."))
            
            return value
        
    def validate_password(self,value):
            if len(value)<8:
                raise serializers.ValidationError(_("Password must be at least 8 characters long."))
            
            return value
        
    def create(self, validated_data):
            addresses_data = validated_data.pop('addresses', [])
            user = User.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            
            # Create or reuse addresses
            for address_data in addresses_data:
                address, created = Address.objects.get_or_create(
                    user=user,
                    country=address_data['country'],
                    region=address_data['region'],
                    city=address_data.get('city', ''),  
                    kebele=address_data['kebele'],
                    street=address_data['street'],
                    latitude=address_data['latitude'],
                    longitude=address_data['longitude']
                )
 
                if address_data.get('is_current'):
                    Address.objects.filter(user=user, is_current=True).update(is_current=False)
                    address.is_current = True
                    address.save()
                
            if user.user_type =='professional':
                professional_profile = ProfessionalProfile.objects.create(user = user)
                professional_profile.save()
                
            if user.user_type =='customer':
                customer_profile = CustomerProfile.objects.create(user = user)
                customer_profile.save()
            if user.user_type =='admin':
                admin_profile = AdminProfile.objects.create(user=user)
                admin_profile.save()               

            return user

            
    def update(self, instance, validated_data):
            addresses_data = validated_data.pop('addresses', None)
            email = validated_data.pop('email')

            # Update user fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update addresses if provided
            if addresses_data is not None:
                for address_data in addresses_data:
                    address, created = Address.objects.get_or_create(
                        user=instance,
                        country=address_data['country'],
                        region=address_data['region'],
                        city=address_data.get('city', ''),
                        kebele=address_data['kebele'],
                        street=address_data['street'],
                        latitude=address_data['latitude'],
                        longitude=address_data['longitude']
                    )
                    
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
        
class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = AdminProfile
        fields = ['user', 'permissions', 'admin_level']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            print('context is',self.context)

            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True,context=self.context)
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
    admin = AdminProfileSerializer()

    class Meta:
        model = AdminLog
        fields = ['admin', 'action', 'timestamp']
        
        
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerProfile
        fields = ['user', 'rating']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True,context={
                'request':self.request
            })
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
            customer_profile = CustomerProfile.objects.create(user=user, **validated_data)
            return customer_profile


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'school', 'degree', 'field_of_study', 'location',
            'document_url', 'start_date', 'end_date', 'honors',
            'is_current_student'
        ]

    def create(self, validated_data):
        return Education.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# Portfolio Serializer
class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'description', 'image', 'video_url',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        return Portfolio.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'id', 'name', 'issued_by', 'document_url', 'date_issued',
            'expiration_date', 'certificate_type', 'is_renewable', 
            'renewal_period'
        ]

    def create(self, validated_data):
        return Certificate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    skills = SkillSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    portfolios = PortfolioSerializer(many=True, required=False)
    certificates = CertificateSerializer(many=True, required=False)
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = ProfessionalProfile
        fields = [
            'user', 'skills', 'educations', 'portfolios', 'certificates', 'categories',
            'is_verified', 'business_logo', 'business_card', 'rating', 
            'years_of_experience', 'portfolio_url', 'is_available', 'bio'
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        skills_data = validated_data.pop('skills', [])
        educations_data = validated_data.pop('educations', [])
        portfolios_data = validated_data.pop('portfolios', [])
        certificates_data = validated_data.pop('certificates', [])
        categories_data = validated_data.pop('categories', [])

        with transaction.atomic():
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

            professional_profile = ProfessionalProfile.objects.create(user=user, **validated_data)

            self._create_or_update_related_objects(
                professional_profile, 
                skills_data, 
                categories_data, 
                educations_data, 
                portfolios_data, 
                certificates_data, 
                is_update=False
            )

        return professional_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        skills_data = validated_data.pop('skills', [])
        categories_data = validated_data.pop('categories', [])
        educations_data = validated_data.pop('educations', [])
        portfolios_data = validated_data.pop('portfolios', [])
        certificates_data = validated_data.pop('certificates', [])
        
        # Update user
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Handle portfolios (create or update)
        if portfolios_data:
            # instance.portfolios.all().delete()  # Delete existing portfolios
            for portfolio_data in portfolios_data:
                portfolio_id = portfolio_data.get('id')
                if portfolio_id:
                    portfolio = Portfolio.objects.filter(id=portfolio_id).first()
                    if portfolio:
                        portfolio_serializer = PortfolioSerializer(instance=portfolio, data=portfolio_data, partial=True)
                        portfolio_serializer.is_valid(raise_exception=True)
                        portfolio_serializer.save(professional=instance)
                    else:
                        # Create a new portfolio
                        portfolio_serializer = PortfolioSerializer(data=portfolio_data)
                        portfolio_serializer.is_valid(raise_exception=True)
                        portfolio_serializer.save(professional=instance)
                else:
                    # Create a new portfolio if no ID provided
                    portfolio_serializer = PortfolioSerializer(data=portfolio_data)
                    portfolio_serializer.is_valid(raise_exception=True)
                    portfolio_serializer.save(professional=instance)

        # Handle skills (create or update)
        if skills_data:
            instance.skills.clear()  # Remove existing skills
            for skill_data in skills_data:
                skill_id = skill_data.get('id')
                if skill_id:
                    skill = Skill.objects.filter(id=skill_id).first()
                    if skill:
                        # Update existing skill
                        skill_serializer = SkillSerializer(instance=skill, data=skill_data, partial=True)
                        skill_serializer.is_valid(raise_exception=True)
                        skill_serializer.save()
                    else:
                        # Create a new skill
                        skill_serializer = SkillSerializer(data=skill_data)
                        skill_serializer.is_valid(raise_exception=True)
                        skill_serializer.save()
                else:
                    # Create a new skill if no ID provided
                    skill_serializer = SkillSerializer(data=skill_data)
                    skill_serializer.is_valid(raise_exception=True)
                    skill_serializer.save()

        # Handle educations (create or update)
        if educations_data:
            instance.educations.all().delete()  # Delete existing educations
            for education_data in educations_data:
                education_id = education_data.get('id')
                if education_id:
                    education = Education.objects.filter(id=education_id).first()
                    if education:
                        # Update existing education
                        education_serializer = EducationSerializer(instance=education, data=education_data, partial=True)
                        education_serializer.is_valid(raise_exception=True)
                        education_serializer.save()
                    else:
                        # Create a new education
                        education_serializer = EducationSerializer(data=education_data)
                        education_serializer.is_valid(raise_exception=True)
                        education_serializer.save(professional=instance)
                else:
                    # Create a new education if no ID provided
                    education_serializer = EducationSerializer(data=education_data)
                    education_serializer.is_valid(raise_exception=True)
                    education_serializer.save(professional=instance)

        # Handle certificates (create or update)
        if certificates_data:
            instance.certificates.all().delete()  # Delete existing certificates
            for certificate_data in certificates_data:
                certificate_id = certificate_data.get('id')
                if certificate_id:
                    certificate = Certificate.objects.filter(id=certificate_id).first()
                    if certificate:
                        # Update existing certificate
                        certificate_serializer = CertificateSerializer(instance=certificate, data=certificate_data, partial=True)
                        certificate_serializer.is_valid(raise_exception=True)
                        certificate_serializer.save()
                    else:
                        # Create a new certificate
                        certificate_serializer = CertificateSerializer(data=certificate_data)
                        certificate_serializer.is_valid(raise_exception=True)
                        certificate_serializer.save(professional=instance)
                else:
                    # Create a new certificate if no ID provided
                    certificate_serializer = CertificateSerializer(data=certificate_data)
                    certificate_serializer.is_valid(raise_exception=True)
                    certificate_serializer.save(professional=instance)

        # Handle categories (create or update)
        if categories_data:
            instance.categories.clear()  # Remove existing categories
            for category_data in categories_data:
                category_id = category_data.get('id')
                if category_id:
                    category = Category.objects.filter(id=category_id).first()
                    if category:
                        # Update existing category
                        category_serializer = CategorySerializer(instance=category, data=category_data, partial=True)
                        category_serializer.is_valid(raise_exception=True)
                        category_serializer.save()
                    else:
                        # Create a new category
                        category_serializer = CategorySerializer(data=category_data)
                        category_serializer.is_valid(raise_exception=True)
                        category_serializer.save()
                else:
                    # Create a new category if no ID provided
                    category_serializer = CategorySerializer(data=category_data)
                    category_serializer.is_valid(raise_exception=True)
                    category_serializer.save()

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
