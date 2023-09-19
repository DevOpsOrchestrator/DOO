from django.urls import path

from . import views

app_name = 'doo'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # Ticket urls
    path('ticket/',views.TicketListView.as_view(), name='ticket'),
    path('ticket/<pk>',views.TicketDetailView.as_view(), name='ticket_detail'),
    path('ticket/add/',views.TicketCreateView.as_view(), name='ticket_add'),
    path('ticket/edit/<pk>',views.TicketUpdateView.as_view(), name='ticket_edit'),
    path('ticket/del/<pk>',views.TicketDeleteView.as_view(), name='ticket_del'),
    
    # Template urls
    path('template/', views.TemplateListView.as_view(), name='template'),                   # All templates
    path('template/<pk>', views.TemplateDetailView.as_view(), name='template_detail'),      # Selected template
    path('template/add/', views.TemplateCreateView.as_view(), name='template_add'),         # Add new template
    path('template/edit/<pk>', views.TemplateUpdateView.as_view(), name='template_edit'),   # Edit selected template
    path('template/del/<pk>', views.TemplateDeleteView.as_view(), name='template_del'),     # Delete selected template
    
    # Team urls
    path('team/', views.TeamListView.as_view(), name='team'),                   # All teams
    path('team/<pk>', views.TeamDetailView.as_view(), name='team_detail'),      # Selected team
    path('team/add/', views.TeamCreateView.as_view(), name='team_add'),         # Add new team
    path('team/edit/<pk>', views.TeamUpdateView.as_view(), name='team_edit'),   # Edit selected team
    path('team/del/<pk>', views.TeamDeleteView.as_view(), name='team_del'),     # Delete selected team

    # Group urls
    path('group/', views.GroupListView.as_view(), name='group'),                   # All groups
    path('group/<pk>', views.GroupDetailView.as_view(), name='group_detail'),      # Selected group
    path('group/add/', views.GroupCreateView.as_view(), name='group_add'),         # Add new group
    path('group/edit/<pk>', views.GroupUpdateView.as_view(), name='group_edit'),   # Edit selected group
    path('group/del/<pk>', views.GroupDeleteView.as_view(), name='group_del'),     # Delete selected group

    # Service urls
    path('service/', views.ServiceListView.as_view(), name='service'),                   # All services
    path('service/<pk>', views.ServiceDetailView.as_view(), name='service_detail'),      # Selected service
    path('service/<pk>/templates', views.ServiceTemplateListView.as_view(), 
                                          name='service_templates_detail'),              # Templates in Service
    path('service/add/', views.ServiceCreateView.as_view(), name='service_add'),         # Add new service
    path('service/edit/<pk>', views.ServiceUpdateView.as_view(), name='service_edit'),   # Edit selected service
    path('service/del/<pk>', views.ServiceDeleteView.as_view(), name='service_del'),     # Delete selected service

    # Template urls
    path('template/', views.TemplateListView.as_view(), name='template'),                   # All templates
    path('template/<pk>', views.TemplateDetailView.as_view(), name='template_detail'),      # Selected template
    path('template/add/', views.TemplateCreateView.as_view(), name='template_add'),         # Add new template
    path('template/edit/<pk>', views.TemplateUpdateView.as_view(), name='template_edit'),   # Edit selected template
    path('template/del/<pk>', views.TemplateDeleteView.as_view(), name='template_del'),     # Delete selected template

    # Provision urls
    path('provision/<int:idTicket>', views.ProvisionStart.as_view(), name='provision_start'), 
    
    # Report urls
    path('report/', views.TeamReportView.as_view(), name='report'),

    # Catalog urls
    path('catalog/', views.CatalogView.as_view(), name='catalog'), 
]   

