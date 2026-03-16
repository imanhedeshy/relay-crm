import uuid

from django.db import models


class Role(models.TextChoices):
    PARENT_ADMIN = "PARENT_ADMIN", "Parent admin"
    CHILD_MANAGER = "CHILD_MANAGER", "Child manager"
    SALES_REP = "SALES_REP", "Sales rep"
    VIEWER = "VIEWER", "Viewer"


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ["full_name"]


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="memberships", on_delete=models.CASCADE)
    company_id = models.UUIDField()
    role = models.CharField(max_length=32, choices=Role.choices)

    class Meta:
        unique_together = ("user", "company_id", "role")
        ordering = ["role", "company_id"]
