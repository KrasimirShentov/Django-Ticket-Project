from rest_framework import serializers
 
from .models import Ticket
 
 
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        # TODO: add 'assignee', 'creator', 'sprint' when the FKs are enabled
        fields = ['id', 'title', 'description', 'estimation', 'priority', 'created_at', 'updated_at']
        # TODO: add 'creator' here - it is set from request.user, never by the client
        read_only_fields = ['id', 'created_at', 'updated_at']
 
    # estimation >= 0 and priority in (low, medium, high) are validated automatically by DRF
    # (PositiveIntegerField and TextChoices). Extra rules go below.
 
    # TODO: enable with the sprint FK - no new tickets in a closed sprint
    # def validate_sprint(self, sprint):
    #     if sprint is None:
    #         return sprint
    #     moving_to_new_sprint = self.instance is None or self.instance.sprint_id != sprint.id
    #     if sprint.status == 'closed' and moving_to_new_sprint:
    #         raise serializers.ValidationError('Cannot assign a ticket to a closed sprint.')
    #     return sprint
 