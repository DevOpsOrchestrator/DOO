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

# Provision
router.register('provision', views.ProvisionViewSet)

urlpatterns = [
    path('provision/template/<pk>',views.TemplateProvisionViewSet.as_view(),name='provision_template_add'),
    path('provision/template/<pk>/itens',views.TemplateProvisionItensViewSet.as_view(),name='provision_template_itens_detail'),
]

urlpatterns += router.urls