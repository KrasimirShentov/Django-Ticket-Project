from rest_framework import serializers

from .models import Sprint, Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'assignee', 'creator',
            'estimation', 'priority', 'status', 'sprint', 'created_at', 'updated_at',
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

class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get(
            'start_date',
            self.instance.start_date if self.instance else None)
        
        end_date = attrs.get(
            'end_date',
            self.instance.end_date if self.instance else None)

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                'End date must be after start_date date'
            )

        return attrs