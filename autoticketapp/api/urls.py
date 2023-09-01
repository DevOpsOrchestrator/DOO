from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'autoticket-api'

router = DefaultRouter()
router.APIRootView = views.AutoTicketRootView

# Ticket
router.register('ticket', views.TicketViewSet)

# Team
router.register('team', views.TeamViewSet)

# Group
router.register('group', views.GroupViewSet)

# Service
router.register('service', views.ServiceViewSet)

# Template
router.register('template', views.TemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]