import os
import uuid
from django.db import models
from django.utils import timezone

class Webhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

class Website(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    expected_status_code = models.IntegerField(default=200)
    created_at = models.DateTimeField(auto_now_add=True)
    associated_webhooks = models.ManyToManyField(Webhook, blank=True)

    def __str__(self):
        return self.url

    def get_webhooks(self):
        webhooks = self.associated_webhooks.all()
        if webhooks.exists():
            return [webhook.url for webhook in webhooks]

        default_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        return [default_webhook] if default_webhook else []

class StatusLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=10, choices=[("up", "UP"), ("down", "DOWN")])
    response_time = models.FloatField(null=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    last_status_change = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.website.url} - {self.status} at {self.checked_at}"
