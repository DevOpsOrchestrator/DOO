from typing import Any
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.views.generic.edit import FormView
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

from .forms import TemplateForm

from django.contrib.auth.mixins import PermissionRequiredMixin



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
    permission_required = 'dooapp.view_ticket'
    model = Ticket
    table_class = TicketTable
    template_name = 'dooapp/ticket_list.html'
    ordering = ['-id']

class TicketCreateView(CreateView):
    permission_required = 'dooapp.add_ticket'
    model = Ticket
    fields = ["numero","titulo","descricao","prioridade"]
    template_name = "dooapp/ticket_form.html"

class TicketUpdateView(UpdateView):
    permission_required = 'doo.change_ticket'
    model = Ticket
    fields = ["numero","titulo","descricao","prioridade"]
    template_name = "dooapp/ticket_form.html"

class TicketDeleteView(DeleteView):
    permission_required = 'doo.delete_ticket'
    model = Ticket
    template_name = "dooapp/confirm_delete.html"

"""
    Classes refering to the Team views
"""

TEAM_URL = '/doo/team'

class TeamDetailView (DetailView):
    model = Team

class TeamListView(TableView):
    permission_required = 'dooapp.view_team'
    model = Team
    table_class = TeamTable
    template_name = 'dooapp/team_list.html'

class TeamCreateView(CreateView):
    permission_required = 'doo.add_team'
    model = Team
    fields = ["nome"]
    template_name = "dooapp/team_form.html"
    success_url = TEAM_URL

class TeamUpdateView(UpdateView):
    permission_required = 'doo.change_team'
    model = Team
    fields = ["nome"]
    template_name = "dooapp/team_form.html"
    success_url = TEAM_URL

class TeamDeleteView(DeleteView):
    permission_required = 'doo.delete_team'
    model = Team
    template_name = "dooapp/confirm_delete.html"
    success_url = TEAM_URL
    
"""
    Classes refering to the Group views
"""  

GROUP_URL = '/doo/group'

class GroupDetailView (DetailView):
    model = Group

class GroupListView(TableView):
    permission_required = 'dooapp.view_group'
    model = Group
    table_class = GroupTable
    template_name = 'dooapp/group_list.html'

class GroupCreateView(CreateView):
    permission_required = 'doo.add_group'
    model = Group
    fields = ["nome", "equipe"]
    template_name = "dooapp/group_form.html"
    success_url = GROUP_URL

class GroupUpdateView(UpdateView):
    permission_required = 'doo.change_group'
    model = Group
    fields = ["nome", "equipe"]
    template_name = "dooapp/group_form.html"
    success_url = GROUP_URL

class GroupDeleteView(DeleteView):
    permission_required = 'doo.delete_group'
    model = Group
    template_name = "dooapp/confirm_delete.html"
    success_url = GROUP_URL
   
"""
    Classes refering to the Group views
"""  
SERVICE_URL = '/doo/service'

class ServiceDetailView (DetailView):
    model = Service

class ServiceListView(TableView):
    permission_required = 'dooapp.view_service'
    model = Service
    table_class = ServiceTable
    template_name = 'dooapp/service_list.html'

class ServiceCreateView(CreateView):
    permission_required = 'doo.add_service'
    model = Service
    fields = ["nome", "status","grupo"]
    template_name = "dooapp/service_form.html"
    success_url = SERVICE_URL

class ServiceUpdateView(UpdateView):
    permission_required = 'doo.change_service'
    model = Service
    fields = ["nome", "status", "grupo"]
    template_name = "dooapp/service_form.html"
    success_url = SERVICE_URL

class ServiceDeleteView(DeleteView):
    permission_required = 'doo.delete_service'
    model = Service
    template_name = "dooapp/confirm_delete.html"
    success_url = SERVICE_URL
   
   
"""
    Classes refering to the Template views
"""

TEMPLATE_URL = '/doo/template/'

class TemplateDetailView (DetailView):
    model = Template

class TemplateListView(TableView):
    permission_required = 'doo.view_template'
    model = Template
    table_class = TemplateTable
    template_name = 'dooapp/template_list.html'

class TemplateCreateView(CreateView):
    model = Template
    form_class = TemplateForm
    permission_required = 'dooapp.add_template'
    template_name = "dooapp/template_form.html"
    success_url = TEMPLATE_URL
    
    def get_success_url(self) -> str:
        return super().get_success_url()
    

class TemplateUpdateView(UpdateView):
    permission_required = 'doo.change_template'
    model = Template
    fields = ["titulo", "codigo"]
    template_name = "dooapp/template_form.html"
    success_url = TEMPLATE_URL

class TemplateDeleteView(DeleteView):
    permission_required = 'doo.delete_template'
    model = Template
    template_name = "dooapp/confirm_delete.html"
    success_url = TEMPLATE_URL

"""
    Classes refering to the Provision views
"""

class ProvisionStart(View):
    template_name = 'dooapp/provision.html'

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
    template_name = 'dooapp/report.html'
    
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
    template_name = 'dooapp/catalog.html'

    def get(self, request):

        teams = RestrictedQuerySet(model=Team).all()

        return render(request, self.template_name, {
            'teams': teams,
        })
