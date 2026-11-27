from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
# TODO: replace IsAdminUser with IsAdmin from users.permissions once it exists
# (an admin is a user with is_staff=True, which is what IsAdminUser checks)
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .filters import TicketFilter, SprintFilter
from .models import Ticket, Sprint
from .serializers import TicketSerializer, SprintSerializer

class TicketPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('assignee', 'creator', 'sprint')
    serializer_class = TicketSerializer
    pagination_class = TicketPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TicketFilter

    def get_permissions(self):
        # everyone logged in may read; only admins may create / update / delete
        if self.action in ('list', 'retrieve', 'backlog'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminUser()]

    def perform_create(self, serializer):
        # the creator is always the authenticated user
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=['get'])
    def backlog(self, request):
        """Backlog = tickets without a sprint."""
        queryset = self.filter_queryset(self.get_queryset().filter(sprint__isnull=True))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class SprintViewSet(viewsets.ModelViewSet):
    queryset = Sprint.objects.select_related('created_by')
    serializer_class = SprintSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = SprintFilter

    pagination_class = TicketPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )