import uuid

from django.db import models


class CompanyType(models.TextChoices):
    PARENT = "PARENT", "Parent"
    CHILD = "CHILD", "Child"


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=16, choices=CompanyType.choices)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
