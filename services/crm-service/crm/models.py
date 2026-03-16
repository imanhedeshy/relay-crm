import uuid

from django.db import models


class LeadStatus(models.TextChoices):
    NEW = "NEW", "New"
    QUALIFIED = "QUALIFIED", "Qualified"


class AsyncStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class ActivityKind(models.TextChoices):
    FOLLOW_UP = "FOLLOW_UP", "Follow-up"
    NOTE = "NOTE", "Note"
    WORKFLOW_ERROR = "WORKFLOW_ERROR", "Workflow error"


class DealStage(models.TextChoices):
    DISCOVERY = "DISCOVERY", "Discovery"
    PROPOSAL = "PROPOSAL", "Proposal"
    WON = "WON", "Won"


class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField()
    created_by_user_id = models.UUIDField()
    title = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    status = models.CharField(max_length=32, choices=LeadStatus.choices, default=LeadStatus.NEW)
    scoring_status = models.CharField(max_length=32, choices=AsyncStatus.choices, default=AsyncStatus.PENDING)
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, related_name="activities", on_delete=models.CASCADE)
    company_id = models.UUIDField()
    kind = models.CharField(max_length=32, choices=ActivityKind.choices)
    note = models.TextField()
    workflow_event_id = models.UUIDField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Deal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField()
    name = models.CharField(max_length=255)
    stage = models.CharField(max_length=32, choices=DealStage.choices)
    value_cents = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
