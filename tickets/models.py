from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

class Ticket(models.Model):
    pass

class Sprint(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_sprints"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                "End date cannot be set before start date"
            )

    def __str__(self):
        return self.name
