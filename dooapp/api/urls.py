from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'doo-api'

router = DefaultRouter()
router.APIRootView = views.dooRootView

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

# FormItens
router.register('formitens', views.FormItensViewSet)

urlpatterns = [
    path('', include(router.urls)),
]