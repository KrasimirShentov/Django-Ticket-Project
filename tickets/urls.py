from rest_framework.routers import DefaultRouter

from .views import TicketViewSet, SprintViewSet

router = DefaultRouter()
router.register('tickets', TicketViewSet, basename='ticket')
router.register('sprints', SprintViewSet, basename='sprint')

urlpatterns = router.urls
