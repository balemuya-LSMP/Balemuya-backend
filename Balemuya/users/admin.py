from django.contrib import admin
from .models import User, Address

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1 
    fields = ['country', 'region', 'woreda', 'city', 'kebele', 'street', 'latitude', 'longitude', 'is_current']  

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = [
        'email', 'first_name', 'middle_name', 'last_name',
        'phone_number', 'gender', 'profile_image', 'kebele_id_image',
        'user_type', 'is_active', 'is_superuser'
    ]
    list_filter = [
        'user_type', 'email', 'first_name', 'middle_name',
        'last_name', 'phone_number', 'gender', 'is_active'
    ]
    search_fields = [
        'email', 'first_name', 'middle_name', 'last_name',
        'phone_number', 'gender'
    ]
    inlines = [AddressInline] 

class AddressAdmin(admin.ModelAdmin):
    model = Address
    list_display = [
        'user', 'country', 'region', 'woreda', 
        'city', 'kebele', 'street', 'latitude', 
        'longitude', 'is_current'
    ]
    search_fields = [
        'country', 'region', 'woreda', 'city', 
        'kebele', 'street'
    ]

admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)