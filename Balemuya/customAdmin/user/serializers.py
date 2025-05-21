from rest_framework import serializers
from users.models import Professional, User,Customer,Admin
from common.serializers import AddressSerializer

class ProfessionalListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    profile_image = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source='user.entity_type')
    user_type=serializers.CharField(source='user.user_type')
    is_blocked = serializers.BooleanField(source='user.is_blocked')
    is_active = serializers.BooleanField(source='user.is_active')
    created_at = serializers.DateTimeField(source='user.created_at')
    updated_at = serializers.DateTimeField(source='user.updated_at')

    class Meta:
        model = Professional
        fields = [
            'id',
            'full_name',
            'username',
            'email',
            'phone_number',
            'profile_image',
            'rating',
            'address',
            'entity_type',
            'user_type',
            'is_verified',
            'is_available',
            'is_blocked',
            'is_active',
            'created_at',
            'updated_at',
            
        ]

    def get_full_name(self, obj):
        if obj.user.entity_type =='individual':
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.entity_type =='organization':
            return f"{obj.user.org_name}"
    
    def get_address(self,obj):
        if obj.user.address:
            return AddressSerializer(obj.user.address).data
        return None

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile_image:
            image_url = obj.user.profile_image.url
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return None
    
    



class CustomerListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    profile_image = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source='user.entity_type')
    user_type = serializers.CharField(source='user.user_type')
    is_blocked = serializers.BooleanField(source='user.is_blocked')
    is_active = serializers.BooleanField(source='user.is_active')
    address = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'username', 'email', 'phone_number', 
            'profile_image', 'address', 'entity_type', 'user_type',
            'is_blocked', 'is_active', 'rating', 'description', 
            'number_of_employees', 'number_of_services_booked', 'report_count'
        ]
        read_only_fields = ['id', 'number_of_services_booked']

    def get_full_name(self, obj):
        if obj.user.entity_type =='individual':
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.entity_type =='organization':
            return f"{obj.user.org_name}"

            

    def get_profile_image(self, obj):
        """Returns the absolute URL for the profile image."""
        request = self.context.get('request')
        if obj.user.profile_image:
            image_url = obj.user.profile_image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None
    
    def get_address(self, obj):
        """Returns serialized address data if available."""
        if obj.user.address:
            return AddressSerializer(obj.user.address).data
        return None

    def to_representation(self, instance):
        """Customize the fields based on entity type."""
        rep = super().to_representation(instance)
        if instance.user.entity_type == 'individual':
            rep.pop('number_of_employees', None)
        return rep
    
    
    

class AdminListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id')
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    profile_image = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source='user.entity_type')
    user_type = serializers.CharField(source='user.user_type')
    is_blocked = serializers.BooleanField(source='user.is_blocked')
    is_active = serializers.BooleanField(source='user.is_active')
    address = serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = [
            'id', 'full_name', 'username', 'email', 'phone_number',
            'profile_image', 'is_blocked', 'entity_type','user_type','is_active','address'
        ]
        read_only_fields = ['id']

    def get_full_name(self, obj):
        if obj.user.user_type =='admin':
            return f"{obj.user.first_name} {obj.user.last_name}"

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile_image:
            image_url = obj.user.profile_image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None

    def get_address(self, obj):
        if obj.user.address:
            return AddressSerializer(obj.user.address).data
        return None