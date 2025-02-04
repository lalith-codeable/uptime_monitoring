from django.db import models

class Website(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    check_interval = models.IntegerField(default=300)  #5mins
    expected_status_code = models.IntegerField(default=200)
    created_at = models.DateTimeField(auto_now_add=True)

class StatusLog(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="logs")
    status = models.CharField(max_length=10, choices=[("up", "UP"), ("down", "DOWN")])
    response_time = models.FloatField(null=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    last_status_change = models.DateTimeField()
