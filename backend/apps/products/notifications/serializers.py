from rest_framework import serializers
from .models import AdminNotification


class AdminNotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AdminNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "url",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "url",
            "created_at",
        ]