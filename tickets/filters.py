import django_filters

from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    class Meta:
        model = Ticket
        # TODO: add 'assignee' and 'sprint' when the FKs are enabled
        fields = ['priority']
