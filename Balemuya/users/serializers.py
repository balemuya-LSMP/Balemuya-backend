from rest_framework import serializers

class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)