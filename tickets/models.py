import uuid
from django.conf import settings
from django.db import models

class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    #assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='assigned_tickets')
    #creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_tickets', editable=False)
    estimation = models.PositiveIntegerField()
    priority = models.CharField(max_length=10, choices=Priority.choices)
    #sprint = models.ForeignKey('sprints.Sprint', null=True, blank=True, on_delete=models.SET_NULL, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_backlog(self):
        return self.sprint_id is None
