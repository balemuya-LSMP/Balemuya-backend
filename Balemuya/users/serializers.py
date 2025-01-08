from rest_framework import serializers
from .models import User, Address, Permission, AdminProfile, AdminLog, CustomerProfile, Skill, ProfessionalProfile, Education, Portfolio, Certificate

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'gender', 'email', 'phone_number', 'profile_image', 'kebele_id_image', 'user_type', 'bio', 'last_login', 'created_at', 'addresses']


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
        
class AdminLogSerializer(serializers.ModelSerializer):
    admin = AdminProfileSerializer()

    class Meta:
        model = AdminLog
        fields = ['admin', 'action', 'timestamp']
        
        
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerProfile
        fields = ['user', 'rating', 'total_interactions']
        
class ProfessionalProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer() 
    skills = SkillSerializer(many=True)

    class Meta:
        model = ProfessionalProfile
        fields = ['user', 'skills', 'is_verified', 'business_logo', 'business_card', 'rating', 'years_of_experience', 'portfolio_url', 'availability']



class EducationSerializer(serializers.ModelSerializer):
    professional = ProfessionalProfileSerializer()

    class Meta:
        model = Education
        fields = ['professional', 'school', 'degree', 'field_of_study', 'location', 'document_url', 'start_date', 'end_date', 'honors', 'is_current_student']

# Portfolio Serializer
class PortfolioSerializer(serializers.ModelSerializer):
    professional = ProfessionalProfileSerializer()  

    class Meta:
        model = Portfolio
        fields = ['professional', 'title', 'description', 'image', 'video_url', 'created_at', 'updated_at']

# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    professional = ProfessionalProfileSerializer()  
    class Meta:
        model = Certificate
        fields = ['professional', 'name', 'issued_by', 'document_url', 'date_issued', 'expiration_date', 'certificate_type', 'is_renewable', 'renewal_period']