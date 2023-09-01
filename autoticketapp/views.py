from django.views.generic import View
from django.shortcuts import  render, redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import View as RestView

from users.querysets import RestrictedQuerySet

from users.utilities.view import TableView, CreateView, UpdateView, DeleteView, DetailView
from .models import (
    Ticket,
    Team,
    Group,
    Service,
    Template,
)
from .tables import (
    TicketTable,
    TeamTable,
    GroupTable,
    ServiceTable,
    TemplateTable,
)

from .report import team_report, ReportSerializer

class HomeView(View):
    template_name = 'base/home.html'

    def get(self, request):
        if  not request.user.is_authenticated:
            url = "{}?next={}".format(reverse('user:login'), request.path )
            return redirect(url)
        
        return render(request, self.template_name, {})

"""
    Classes refering to the ticket views
"""
class TicketDetailView (DetailView):
    model = Ticket

class TicketListView(TableView):
    permission_required = 'autoticketapp.view_ticket'
    model = Ticket
    table_class = TicketTable
    template_name = 'autoticketapp/ticket_list.html'
    ordering = ['-id']

class TicketCreateView(CreateView):
    permission_required = 'autoticketapp.add_ticket'
    model = Ticket
    fields = ["numero","titulo","descricao","prioridade"]
    template_name = "autoticketapp/ticket_form.html"

class TicketUpdateView(UpdateView):
    permission_required = 'autoticket.change_ticket'
    model = Ticket
    fields = ["numero","titulo","descricao","prioridade"]
    template_name = "autoticketapp/ticket_form.html"

class TicketDeleteView(DeleteView):
    permission_required = 'autoticket.delete_ticket'
    model = Ticket
    template_name = "autoticketapp/confirm_delete.html"

"""
    Classes refering to the Team views
"""

TEAM_URL = '/autoticket/team'

class TeamDetailView (DetailView):
    model = Team

class TeamListView(TableView):
    permission_required = 'autoticketapp.view_team'
    model = Team
    table_class = TeamTable
    template_name = 'autoticketapp/team_list.html'

class TeamCreateView(CreateView):
    permission_required = 'autoticket.add_team'
    model = Team
    fields = ["nome"]
    template_name = "autoticketapp/team_form.html"
    success_url = TEAM_URL

class TeamUpdateView(UpdateView):
    permission_required = 'autoticket.change_team'
    model = Team
    fields = ["nome"]
    template_name = "autoticketapp/team_form.html"
    success_url = TEAM_URL

class TeamDeleteView(DeleteView):
    permission_required = 'autoticket.delete_team'
    model = Team
    template_name = "autoticketapp/confirm_delete.html"
    success_url = TEAM_URL
    
"""
    Classes refering to the Group views
"""  

GROUP_URL = '/autoticket/group'

class GroupDetailView (DetailView):
    model = Group

class GroupListView(TableView):
    permission_required = 'autoticketapp.view_group'
    model = Group
    table_class = GroupTable
    template_name = 'autoticketapp/group_list.html'

class GroupCreateView(CreateView):
    permission_required = 'autoticket.add_group'
    model = Group
    fields = ["nome", "equipe"]
    template_name = "autoticketapp/group_form.html"
    success_url = GROUP_URL

class GroupUpdateView(UpdateView):
    permission_required = 'autoticket.change_group'
    model = Group
    fields = ["nome", "equipe"]
    template_name = "autoticketapp/group_form.html"
    success_url = GROUP_URL

class GroupDeleteView(DeleteView):
    permission_required = 'autoticket.delete_group'
    model = Group
    template_name = "autoticketapp/confirm_delete.html"
    success_url = GROUP_URL
   
"""
    Classes refering to the Group views
"""  
SERVICE_URL = '/autoticket/service'

class ServiceDetailView (DetailView):
    model = Service

class ServiceListView(TableView):
    permission_required = 'autoticketapp.view_service'
    model = Service
    table_class = ServiceTable
    template_name = 'autoticketapp/service_list.html'

class ServiceCreateView(CreateView):
    permission_required = 'autoticket.add_service'
    model = Service
    fields = ["nome", "status","grupo"]
    template_name = "autoticketapp/service_form.html"
    success_url = SERVICE_URL

class ServiceUpdateView(UpdateView):
    permission_required = 'autoticket.change_service'
    model = Service
    fields = ["nome", "status", "grupo"]
    template_name = "autoticketapp/service_form.html"
    success_url = SERVICE_URL

class ServiceDeleteView(DeleteView):
    permission_required = 'autoticket.delete_service'
    model = Service
    template_name = "autoticketapp/confirm_delete.html"
    success_url = SERVICE_URL
   
   
"""
    Classes refering to the Template views
"""

TEMPLATE_URL = '/autoticket/template/'

class TemplateDetailView (DetailView):
    model = Template

class TemplateListView(TableView):
    permission_required = 'autoticket.view_template'
    model = Template
    table_class = TemplateTable
    template_name = 'autoticketapp/template_list.html'

class TemplateCreateView(CreateView):
    permission_required = 'autoticketapp.add_template'
    model = Template
    fields = ["titulo", "codigo"]
    template_name = "autoticketapp/template_form.html"
    success_url = TEMPLATE_URL

class TemplateUpdateView(UpdateView):
    permission_required = 'autoticket.change_template'
    model = Template
    fields = ["titulo", "codigo"]
    template_name = "autoticketapp/template_form.html"
    success_url = TEMPLATE_URL

class TemplateDeleteView(DeleteView):
    permission_required = 'autoticket.delete_template'
    model = Template
    template_name = "autoticketapp/confirm_delete.html"
    success_url = TEMPLATE_URL

"""
    Classes refering to the Provision views
"""

class ProvisionStart(View):
    template_name = 'autoticketapp/provision.html'

    def get(self, request, idTicket):
        user = request.user

        ticket = Ticket.objects.get(id=idTicket)

        templates = Template.objects.all()

        return render(request, self.template_name, {
            'ticket': ticket,
            'templates': templates
        })

# View of report generation
class TeamReportView(RestView):
    template_name = 'autoticketapp/report.html'
    
    def get(self, request):
        data = team_report()
        serializer = ReportSerializer(instance=data, many=True)
        
        return render(request, self.template_name, {
            'team': serializer['team'],
            'group_count': serializer['group_count'],
            'service_count': serializer['service_count'],
            'template_count': serializer['template_count'],
        })
class CatalogView(View):
    template_name = 'autoticketapp/catalog.html'

    def get(self, request):

        teams = RestrictedQuerySet(model=Team).all()

        return render(request, self.template_name, {
            'teams': teams,
        })
