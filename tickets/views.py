from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
# TODO: replace IsAdminUser with IsAdmin from users.permissions once it exists
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .filters import TicketFilter
from .models import Ticket
from .serializers import TicketSerializer


class TicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = TicketPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TicketFilter

    def get_permissions(self):
        # everyone logged in may read; only admins may create / update / delete
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]

    # TODO: enable with the creator FK - the creator is always the authenticated user
    # def perform_create(self, serializer):
    #     serializer.save(creator=self.request.user)

    # TODO: enable with the sprint FK - backlog = tickets without a sprint
    # @action(detail=False, methods=['get'])
    # def backlog(self, request):
    #     queryset = self.filter_queryset(self.get_queryset().filter(sprint__isnull=True))
    #     page = self.paginate_queryset(queryset)
    #     serializer = self.get_serializer(page, many=True)
    #     return self.get_paginated_response(serializer.data)
