from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model
from common.serializers import UserSerializer

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(many=True, read_only=True)
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'recipient', 'sender', 'is_read', 'created_at', 'url', 'metadata']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert UUIDs to strings if necessary
        representation['recipient'] = [str(user['id']) for user in representation['recipient']]
        representation['sender'] = str(representation['sender']) if representation['sender'] else None
        
        return representation
    # Get sender's profile image URL
    def get_sender_profile_image_url(self, obj):
        if obj.sender.profile_image:
            request = self.context.get('request')
            # Build the absolute URL using the request context (if available)
            return request.build_absolute_uri(obj.sender.profile_image.url) if request else obj.sender.profile_image.url
        return None

    def create(self, validated_data):
        recipients = validated_data.pop('recipient', [])
        
        # Create the notification object
        notification = Notification.objects.create(**validated_data)
        notification.recipient.set(recipients)
        return notification
