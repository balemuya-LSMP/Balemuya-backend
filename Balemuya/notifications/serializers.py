from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model
from common.serializers import UserSerializer
from uuid import UUID

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'recipient', 'is_read', 'created_at', 'url', 'metadata']

    def create(self, validated_data):
        recipients = list(validated_data.pop('recipient', [])) 

        notification = Notification.objects.create(**validated_data)
        notification.recipient.set(recipients)  

        return notification

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if 'metadata' in representation:
            representation['metadata'] = self.serialize_uuid_fields(representation['metadata'])
        
        return representation

    def serialize_uuid_fields(self, data):
        """Recursively convert UUIDs to strings."""
        if isinstance(data, dict):
            return {key: str(value) if isinstance(value, UUID) else self.serialize_uuid_fields(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.serialize_uuid_fields(item) for item in data]
        return data