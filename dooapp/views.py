"""Views module doapp"""
import os
from django.http import JsonResponse, Http404
from django.views.generic import View
from django.shortcuts import  render, redirect
from django.urls import reverse
from rest_framework.views import View as RestView

from users.querysets import RestrictedQuerySet

from users.utilities.view import TableView, CreateView, UpdateView, DeleteView, DetailView
from .models import (
    Ticket,
    Team,
    Group,
    Service,
    Template,
    Provision
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


class HomeView(View):
    """View Home"""
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
    success_url = '/doo/catalog'
    
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
    success_url = "/doo/catalog"
   
"""
    Classes refering to the Group views
"""  
SERVICE_URL = '/doo/service'

class ServiceDetailView (DetailView):
    model = Service

class ServiceTemplateListView(TableView):
    permission_required = 'doo.view_template'
    model = Template
    table_class = TemplateTable
    template_name = 'dooapp/template_list.html'
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        pk = self.kwargs.get('pk')
        
        self.object_list = queryset.filter(service=pk).order_by('name')
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)

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
    success_url = "/doo/catalog"
   
   
"""
    Classes refering to the Template views
"""

TEMPLATE_URL = '/doo/template/'

class TemplateDetailView (DetailView):
    model = Template
    
    def delete(self, request, *args, **kwargs):
        template = self.get_object()
        
        path = template.get_path_playbook()
        
        if os.path.exists(path):
            os.remove(path)
        
        template.delete()   
        
        return JsonResponse({"delete": True}, safe=False)
    
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

        services = Service.objects.order_by("nome").all()
        
        provisions = Provision.objects.filter(ticket=ticket).order_by('-date').all()

        return render(request, self.template_name, {
            'ticket': ticket,
            'services': services,
            'provisions': provisions
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
