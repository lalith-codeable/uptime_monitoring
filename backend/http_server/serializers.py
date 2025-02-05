from rest_framework import serializers
from .models import Website, StatusLog, Webhook

class StatusLogSerializer(serializers.ModelSerializer):
    response_time_ms = serializers.SerializerMethodField()
    last_checked = serializers.DateTimeField(source="checked_at")

    class Meta:
        model = StatusLog
        fields = ["status", "response_time_ms", "last_checked"]

    def get_response_time_ms(self, obj):
        return obj.response_time * 1000 if obj.response_time is not None else None

class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ["id", "url"]

class WebsiteSerializer(serializers.ModelSerializer):
    associated_webhooks = WebhookSerializer(many=True, required=False)
    logs = StatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Website
        fields = [
            "id",
            "url",
            "name",
            "expected_status_code",
            "created_at",
            "associated_webhooks",
            "logs",
        ]
