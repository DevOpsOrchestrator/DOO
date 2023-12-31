from rest_framework import generics
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ModelViewSet
from users.querysets import RestrictedQuerySet

from rest_framework.views import APIView

from ..models import  Ticket,Team, Group, Service, Template, FormItens, Provision
from . import serializers

from repository.models import InventoryRepository
from ansible.plugins.loader import init_plugin_loader

from ansible import context
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.playbook_executor import PlaybookExecutor
import yaml

from  immutabledict import immutabledict

from ansible.utils.vars import load_extra_vars

from ansible_runner import Runner, RunnerConfig

from rest_framework import status
from django.http import JsonResponse

from dooapp.ansible.callback import CallbackModule

def get_playbook(template):
    
    loader = DataLoader()
    playbook = None
    
    if template.yaml:
        
        # Carregue a string YAML usando o DataLoader
        playbook_yaml = loader.load(template.yaml)

        # Crie um objeto Play com base no conteúdo YAML
        playbook = Play().load(playbook_yaml[0])
        
    else:
        playbook = Play()
        setattr(playbook, 'name', template.name)
        
    return playbook

def get_params(params_dict):
    """Function Get Parameters"""
    params = {}
    for line in params_dict:
        if line.startswith('param__'):
            params_key = line.replace('param__', '')
            if params_dict[line]:
                params[params_key] = params_dict[line]
    return params

class dooRootView(APIRootView):
    """
    Raiz do doo API
    """
    def get_view_name(self):
        return 'doo'


#
# Ticket
#

class TicketViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Ticket).all()
    serializer_class = serializers.TicketSerializer

#
# Team
#

class TeamViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Team).all()
    serializer_class = serializers.TeamSerializer

#
# Group
#

class GroupViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Group).all()
    serializer_class = serializers.GroupTeamSerializer

#
# Service
#

class ServiceViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Service).all()
    serializer_class = serializers.ServiceSerializer
    
#
# Provision
#

class ProvisionViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Provision).order_by('-date').all()
    serializer_class = serializers.ProvisionSerializer
    filterset_fields = ['ticket','template','user']

#
# Template
#

class TemplateViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Template).all()
    serializer_class = serializers.TemplateSerializer
    filterset_fields = ['service']
    
class TemplateProvisionViewSet(APIView):
    queryset = RestrictedQuerySet(model=Template).all()
    
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        
        template = Template.objects.get(id=pk)
        ticket = Ticket.objects.get(id=request.POST['ticket'])
        user = self.request.user
        
        playbook_path = template.get_path_playbook()
        
        extra_vars = []
        
        for param,value in get_params(request.POST.dict()).items():
            extra_vars.append(f'{param}={value}')
            
            
        context.CLIARGS = immutabledict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                                module_path=None, forks=100, remote_user=None, private_key_file=None,
                                ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True,
                                become_method=None, become_user=None, verbosity=True, check=False, start_at_task=None, extra_vars=extra_vars)

        # Crie um objeto PlaybookExecutor e execute o playbook
        inventory_repository = InventoryRepository(template.repository)
        inventory_manager = inventory_repository.inventory
        variable_manager = VariableManager(loader=inventory_repository.loader, inventory=inventory_manager)
        variable_manager._extra_vars = load_extra_vars(loader=inventory_repository.loader)
        
        init_plugin_loader([])
        
        playbook = PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=inventory_manager,
            variable_manager=variable_manager,
            loader=inventory_repository.loader,
            passwords={},
        )
        
        callback = CallbackModule()
        callback.set_option('display_skipped_hosts', True)
        callback.set_option('show_per_host_start', True)
        callback.set_option('display_ok_hosts', True)
        callback.set_option('show_task_path_on_failure', True)
        #callback.set_option('show_custom_stats', True)
        callback.set_option('check_mode_markers', True)
        
        playbook._tqm._stdout_callback = callback
        
        playbook.run()
        
        prompt = callback._return
        
        Provision.objects.create(ticket=ticket, template=template, prompt=' '.join(prompt), user=user)

        return JsonResponse({'prompt': prompt,'ticket':ticket.id}, safe=False)

#
# FormItens
#

class FormItensViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=FormItens).all()
    serializer_class = serializers.FormItensSerializer
    filterset_fields = ['template']
    