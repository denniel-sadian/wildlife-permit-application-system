from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for user notifications."""

    class Meta:
        model = Notification
        fields = [
            'id', 'message', 'url', 'read', 'created_at'
        ]
