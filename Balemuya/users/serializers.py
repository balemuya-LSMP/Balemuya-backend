from rest_framework import serializers

class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    
    # def clean(self):
    #     if not self.latitude or not self.longitude:
    #         raise ValidationError("Latitude and longitude are required.")
        
    #     if not (-90 <= sllf.latitude <= 90):
    #         raise ValidationError("Latitude must be between -90 and 90.")
        
    #     if not (-180 <= self.longitude <= 180):
    #         raise ValidationError("Longitude must be between -180 and 180.")   