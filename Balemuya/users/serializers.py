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
    BankAccount,
    Payment,
    SubscriptionPlan,
    SubscriptionPayment,
    WithdrawalTransaction,
    VerificationRequest,
    Feedback,
    Favorite,
)

from common.models import Category
from common.serializers import CategorySerializer, UserSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'professional', 'created_at']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


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
class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer  
        fields = [
            'user','tx_number',
            'rating', 'description',
            'number_of_employees', 'number_of_services_booked','report_count'
        ]
        read_only_fields = ['number_of_services_booked']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        entity_type = instance.user.entity_type
        if entity_type == 'individual':
            rep.pop('number_of_employees', None)

        return rep

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get('description', instance.description)
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
    categories = CategorySerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Professional
        fields = [
            'user',
            'number_of_employees', 'tx_number', 'description',
            'kebele_id_front_image', 'kebele_id_front_image_url',
            'kebele_id_back_image', 'kebele_id_back_image_url',
            'skills','categories', 'rating', 'years_of_experience',
            'balance', 'num_of_request', 'is_available', 'is_verified',
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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user_type = instance.user.user_type
        entity_type = instance.user.entity_type

        # Only return relevant fields for 'individual' and 'organization' professionals
        if user_type == 'professional':
            if entity_type == 'organization':
                rep.pop('kebele_id_front_image', None)
                rep.pop('kebele_id_back_image', None)
                rep.pop('kebele_id_front_image_url', None)
                rep.pop('kebele_id_back_image_url', None)
                rep.pop('educations', None)

            elif entity_type == 'individual':
                rep.pop('number_of_employees', None)
                rep.pop('tx_number', None)

        return rep

    
    
class BankAccountSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='get_bank_code_display', read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            'id',
            'professional',
            'account_name',
            'account_number',
            'bank_code',
            'bank_name',
            'is_verified',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VerificationRequestSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = VerificationRequest
        fields = ['id', 'user', 'status', 'admin_comment', 'created_at', 'updated_at']
        read_only_fields = ['status', 'admin_comment', 'created_at', 'updated_at']

    def get_user(self, obj):
        return UserSerializer(obj.professional.user, context=self.context).data

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
        fields = ['id', 'customer', 'professional', 'booking', 'amount', 'payment_date', 'payment_status', 'payment_method', 'transaction_id']

class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = ['id', 'subscription_plan', 'professional', 'amount', 'payment_date', 'payment_status', 'payment_method', 'transaction_id']
        
        


class WithdrawalTransactionSerializer(serializers.ModelSerializer):
    professional_email = serializers.EmailField(source='professional.user.email', read_only=True)
    
    class Meta:
        model = WithdrawalTransaction
        fields = ['id', 'professional', 'professional_email', 'amount', 'tx_ref', 'status', 'created_at', 'updated_at']
        read_only_fields = ['professional_email', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Withdrawal amount must be greater than zero.")
        return value

    def validate_professional(self, value):
        try:
            professional = Professional.objects.get(id=value.id)
            if not professional.is_active:
                raise serializers.ValidationError("This professional's account is inactive.")
        except Professional.DoesNotExist:
            raise serializers.ValidationError("Professional not found.")
        return value

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feedback 
        fields = '__all__'