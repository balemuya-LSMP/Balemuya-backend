from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
    User,
    Address,
    Permission,
    Admin,
    AdminLog,
    Customer, 
    Professional,
    Skill,
    Education,
    Portfolio,
    Certificate,
    Payment,
    SubscriptionPlan,
    SubscriptionPayment,
    VerificationRequest,
    Feedback,
)

from common.models import Category
from common.serializers import CategorySerializer, UserSerializer

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class VerificationRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, source='user')

    class Meta:
        model = VerificationRequest
        fields = ['id', 'professional', 'status', 'admin_comment', 'created_at', 'updated_at']
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
        fields = ['user', 'permissions']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._update_permissions(instance, validated_data)
        return instance

    def _update_permissions(self, instance, validated_data):
        if 'permissions' in validated_data:
            instance.permissions.clear()
            for permission_data in validated_data['permissions']:
                permission_serializer = PermissionSerializer(data=permission_data)
                permission_serializer.is_valid(raise_exception=True)
                permission_serializer.save()
                instance.permissions.add(permission_serializer.instance)

class AdminLogSerializer(serializers.ModelSerializer):
    admin = AdminSerializer()

    class Meta:
        model = AdminLog
        fields = ['admin', 'action', 'timestamp']

class CustomerSerializer(serializers.ModelSerializer):  # Updated
    user = UserSerializer()

    class Meta:
        model = Customer  
        fields = ['user','full_name', 'rating','gender','description','number_of_employees', 'number_of_services_booked']
        read_only_fields = ['number_of_services_booked']

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
            individual_customer = Customer.objects.create(user=user, **validated_data)  # Updated
            return individual_customer
        

        
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'school', 'degree', 'field_of_study', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Education.objects.create(**validated_data)

class PortfolioSerializer(serializers.ModelSerializer):
    portfolio_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'image', 'portfolio_image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_portfolio_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class CertificateSerializer(serializers.ModelSerializer):
    certificate_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'image', 'name', 'certificate_image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_certificate_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    kebele_id_front_image_url = serializers.SerializerMethodField()
    kebele_id_back_image_url = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Professional
        fields = [
            'user','gender','full_name','number_of_employees','tx_number','description','kebele_id_front_image',
            'kebele_id_front_image_url', 'kebele_id_back_image', 'kebele_id_back_image_url',
            'skills', 'rating', 'years_of_experience', 'is_available', 'is_verified',
            'educations', 'portfolios', 'certificates'
        ]
        read_only_fields = ['id', 'kebele_id_front_image_url', 'kebele_id_back_image_url']

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
    

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer()
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'professional', 'plan_type', 'duration', 'cost', 'start_date', 'end_date']

class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    professional = ProfessionalSerializer()
    class Meta:
        model = Payment
        fields = ['id', 'customer', 'professional', 'service', 'amount', 'payment_date', 'payment_status', 'payment_method', 'transaction_id']

class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = ['id', 'subscription_plan', 'professional', 'amount', 'payment_date', 'payment_status', 'payment_method', 'transaction_id']

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feedback 
        fields = '__all__'