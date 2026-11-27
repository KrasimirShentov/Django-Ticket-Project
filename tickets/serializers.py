from rest_framework import serializers

from .models import Sprint, Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'assignee', 'creator',
            'estimation', 'priority', 'sprint', 'created_at', 'updated_at',
        ]
        # creator is set from request.user in the view, never by the client
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    # estimation >= 0, priority in (low, medium, high) and "assignee / sprint must exist"
    # are validated automatically by DRF (PositiveIntegerField, TextChoices, ForeignKey).

    def validate_sprint(self, sprint):
        """A ticket cannot be put into a closed sprint (null = backlog is always fine)."""
        if sprint is None:
            return sprint
        moving_to_new_sprint = self.instance is None or self.instance.sprint_id != sprint.id
        if sprint.status == Sprint.Status.CLOSED and moving_to_new_sprint:
            raise serializers.ValidationError('Cannot assign a ticket to a closed sprint.')
        return sprint
