from django.db import models


class ProcessingStatus(models.TextChoices):
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class ProcessedEvent(models.Model):
    event_id = models.UUIDField(unique=True)
    lead_id = models.UUIDField()
    status = models.CharField(max_length=32, choices=ProcessingStatus.choices, default=ProcessingStatus.PROCESSING)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
