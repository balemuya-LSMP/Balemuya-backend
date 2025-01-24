from rest_framework import serializers
from .models import Notification
from common.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    sender_profile_image =serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'recipient','sender', 'message', 'is_read', 'created_at']
        