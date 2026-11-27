import django_filters

from .models import Ticket, Sprint


class TicketFilter(django_filters.FilterSet):
    class Meta:
        model = Ticket
        fields = ['priority', 'assignee', 'status', 'sprint']

class SprintFilter(django_filters.FilterSet):
    class Meta:
        model = Sprint
        fields = ['status', 'created_by']