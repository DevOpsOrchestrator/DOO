"""Class Views Repo"""
import os
import shutil
from typing import Any
from users.utilities.view import TableView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from ansible import context
from ansible.playbook.play_context import PlayContext
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.playbook.play import Play
from ansible.playbook.task import Task
from ansible.playbook.block import Block
from ansible.playbook.handler import Handler
from iac.models import InventoryParameter, PlaybookParameter, AnsibleModule
from iac.views import getHtmlInventoryParameter
from .tables import RepositoryTable
from .models import (Repository)
from .helper import handle_uploaded_file
from dooapp.models import Service,Template
from dooapp.forms import TemplateForm

from ansible.playbook import Playbook

from .constants import ATTRIBUTES_TASK, ATTRIBUTES_PLAYBOOK

import yaml
from .dumper import AnsibleDumperRepository

from django.http import QueryDict

# Classes refering to the Repo views

class RepoDetailView (DetailView):
    """Class Detail Repository View"""
    model = Repository

class RepoListView(TableView):
    """Class List Repositories View"""
    permission_required = 'repository.view_repo'
    model = Repository
    table_class = RepositoryTable
    template_name = 'repository/repo_list.html'
    ordering = ['-id']

class RepoCreateView(CreateView):
    """Class Create Repository View"""
    permission_required = 'repository.add_repo'
    model = Repository
    fields = ["nome", "url", "token", "token_key"]
    template_name = "repository/repo_form.html"
    success_url = "/repository/repo/"
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        path = settings.FOLDER_REPOSITORY+'/'+request.POST['nome']
        
        if os.path.exists(path):
            shutil.rmtree(path)
        
        return super().post(request, *args, **kwargs)

class RepoUpdateView(UpdateView):
    """Class Update Repository View"""
    permission_required = 'repository.change_repo'
    model = Repository
    fields = ["nome", "url", "token", "token_key"]
    template_name = "repository/repo_form.html"
    success_url = "/repository/repo/"

class RepoDeleteView(DeleteView):
    """Class Delete Repository View"""
    permission_required = 'repository.delete_repo'
    model = Repository
    template_name = "users/confirm_delete.html"
    
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        
        repository = self.get_object()
        path = repository.folderRepository()
        
        if os.path.exists(path):
            shutil.rmtree(path)
            
        return super().delete(request, *args, **kwargs)

# Classes refering to the Playbook views

def redirect_main(id):
    """Function Redirect for Main"""
    return redirect(reverse("repository:playbook_detail", args=(id,),))

def get_params(params_dict):
    """Function Get Parameters"""
    params = {}
    for line in params_dict:
        if line.startswith('param__'):
            params_key = line.replace('param__', '')
            if params_dict[line]:
                params[params_key] = params_dict[line]
    return params

def get_input_prefix(params_dict, prefix):
    """Function Get Parameters"""
    params = {}
    for line in params_dict:
        if line.startswith(prefix):
            params_key = line.replace(prefix, '')
            if params_dict[line]:
                params[params_key] = params_dict[line]
    return params

def get_playbook(template):
    
    playbook = template.get_playbook()
        
    if not playbook:
        loader = DataLoader()
        playbook = Playbook(loader=loader)
        play = Play()
        setattr(play, 'name', template.name)
        playbook._entries.append(play)
        
    return playbook

def retirar_nulos(data,listAtrribute=None):
        if listAtrribute:
            return {k: v for k, v in data.items() if v and k in listAtrribute}
        return {k: v for k, v in data.items() if v}

def get_string_playbook(playbook):
    dataPlaybook = []

    validos = retirar_nulos(playbook.serialize(), ATTRIBUTES_PLAYBOOK)
        
    data = {'name':validos.pop('name')}
    data.update(validos)
    roles = []
    for r in playbook.roles:
        roles.append(r._role_name)

    if roles:
        data['roles'] = roles

    dataPlaybook.append(data)
        
    return yaml.dump(dataPlaybook, Dumper=AnsibleDumperRepository, explicit_start=True, explicit_end=True, sort_keys=False, default_flow_style=False, default_style='', allow_unicode=True)

def get_tasks_playbook(playbook):

    json_task = []

    for play in playbook.get_plays():
        for bk in play.tasks:
            for task in bk.block:
                json_task.append({'name': task.name, 'action': task.action, task.action: task.args})
    
    return json_task

class PlaybookDetailView (DetailView):
    """Class Playbook Detail View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()
        services = Service.objects.all().order_by('nome')
        inventory_parameters = InventoryParameter.objects.all().order_by('name')
        playbook_parameters = PlaybookParameter.objects.all().order_by('name')
        ansible_modules = AnsibleModule.objects.all().order_by('name')

        context = {'templates': repository.templates.all(), 'formService': TemplateForm, 'services': services, 'ansibleModules': ansible_modules, 'playbookParameters': playbook_parameters,
                   'inventoryParameters': inventory_parameters, 'playbookRepository': playbook_repository}
        return self.render_to_response(context)

class HandlerDetailView (DetailView):
    """Class Handler Detail View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.GET['playbook']
        filename = request.GET['filename']

        handlers = []
        json_handlers = []
        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        handlers = getattr(play, 'handlers')

        for bc in handlers:
            for hd in bc.block:
                json_handlers.append(
                    {'name': hd.name, 'action': hd.action, hd.action: hd.args})

        return JsonResponse(json_handlers, safe=False)

class TaskDetailView (DetailView):
    """Class Task Detail View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.GET['playbook']
        filename = request.GET['filename']

        tasks = []
        json_task = []
        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        tasks = getattr(play, 'tasks')
        for bk in tasks:
            for task in bk.block:
                json_task.append(
                    {'name': task.name, 'action': task.action, task.action: task.args})

        return JsonResponse(json_task, safe=False)

class AddHandlerPlaybookView(CreateView):
    """Classe Add Handler in Playbook View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.POST['playbook']
        filename = request.POST['filename']
        name = request.POST['name']
        id_module = request.POST['actionSelect']

        ansible_module = AnsibleModule.objects.get(id=id_module)

        params_data = get_params(request.POST.dict())

        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        handler = Handler()
                        setattr(handler, 'name', name)
                        setattr(handler, 'action', ansible_module.name)
                        setattr(handler, 'args', params_data)
                        handlers = getattr(play, 'handlers')
                        handlers.append(handler)
                        setattr(play, 'handlers', handlers)

        playbook_repository.salvarPlaybooks()

        return redirect_main(repository.pk)

class TaskDeleteView(DeleteView):
    """Class Task Delete View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()
        playbook_name = request.GET['playbook']
        filename = request.GET['filename']
        name = request.GET['name']

        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_name == play.get_name():
                        blocks = getattr(play, 'tasks')
                        remover = None
                        for block in blocks:
                            for task in block.get_tasks():
                                if name in task.name:
                                    remover = block
                        blocks.remove(remover)
                        setattr(play, 'tasks', blocks)

        playbook_repository.salvarPlaybooks()

        return redirect_main(repository.pk)

class TaskTemplateDetailView (DetailView):
    """Class Task Detail View"""
    model = Template
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        template = self.get_object()
        playbook = get_playbook(template)
        
        json_task = get_tasks_playbook(playbook)

        return JsonResponse(json_task, safe=False)

class TaskTemplateDeleteView(DeleteView):
    """Class Task Delete View"""
    model = Template
    template_name = "repository/playbook_form.html"
    
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        template = self.get_object()
        playbook = get_playbook(template)
        
        params = QueryDict(request.body)
        deleteTask = params.get('task')
        
        for play in playbook.get_plays():
            blocks = getattr(play, 'tasks')
            remover = None
            for block in blocks:
                for task in block.get_tasks():
                    if deleteTask in task.name:
                        remover = block
                        blocks.remove(remover)
                    
        setattr(playbook._entries[0], 'tasks', blocks)
        
        template.playbook = playbook
        template.salvarPlaybook()
        
        template.save() 
        
        json_task = get_tasks_playbook(playbook)

        return JsonResponse(json_task, safe=False)

class AddTaskTemplateView(CreateView):
    """Class Task in Template View"""
    model = Template
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        template = self.get_object()
        
        playbook = get_playbook(template)

        name = request.POST['name']
        id_module = request.POST['actionSelect']

        ansible_module = AnsibleModule.objects.get(id=id_module)        

        params_data = get_params(request.POST.dict())
            
        tasks = []
                  
        block = Block()
        task = Task()
        setattr(task, 'name', name)
        setattr(task, 'action', ansible_module.name)
        setattr(task, 'args', params_data)
        setattr(block,'block',[task])
        tasks = getattr(playbook._entries[0], 'tasks')
        tasks.append(block)
        setattr(playbook._entries[0], 'tasks', tasks)
        
        template.playbook = playbook
        template.salvarPlaybook()
        
        template.save()
        
        json_tasks = get_tasks_playbook(playbook)

        return JsonResponse(json_tasks, safe=False)
    
class AddHostTaskTemplateView(CreateView):
    """Class Task in Template View"""
    model = Template
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        template = self.get_object()
        
        playbook = get_playbook(template)        

        hosts = request.POST.getlist('hosts[]')
        groups = request.POST.getlist('groups[]')

        for play in playbook.get_plays():
            if hosts:
                setattr(play, 'hosts', ','.join(hosts))
            else:
                setattr(play, 'hosts', ','.join(groups))

        template.playbook = playbook
        template.salvarPlaybook()
        
        url = reverse('repository:playbook_detail', kwargs={'pk':template.repository.pk})

        return JsonResponse({'redirect': url}, safe=False)

class AddTaskPlaybookView(CreateView):
    """Class Add Task in Playbook View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.POST['playbook']
        filename = request.POST['filename']
        name = request.POST['name']
        id_module = request.POST['actionSelect']

        notifications = []
        if 'notify[]' in request.POST:
            for notify in request.POST.getlist('notify[]'):
                notifications.append(notify)

        ansible_module = AnsibleModule.objects.get(id=id_module)

        params_data = get_params(request.POST.dict())

        tasks = []
        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        block = Block()
                        task = Task()
                        setattr(task, 'name', name)
                        setattr(task, 'action', ansible_module.name)
                        setattr(task, 'args', params_data)
                        setattr(task, 'notify', notifications)
                        setattr(block,'block',[task])
                        tasks = getattr(play, 'tasks')
                        tasks.append(block)
                        setattr(play, 'tasks', tasks)

        playbook_repository.salvarPlaybooks()

        return redirect_main(repository.pk)

class AddVarsPlaybookView(CreateView):
    """Class Add Vars In Playbook View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.POST['playbook']
        filename = request.POST['filename']

        params_data = get_params(request.POST.dict())

        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        for key, value in params_data.items():
                            if value in ('true', 'false'):
                                value = bool(value)
                            setattr(play, key, value)

        playbook_repository.salvarPlaybooks()
        
        return redirect_main(repository.pk)
    
class AddHostPlaybookView(CreateView):
    """Class Add Host in Playbook View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        playbook_host = request.POST['playbook']
        filename = request.POST['filename']
        hosts = request.POST.getlist('hosts[]')
        groups = request.POST.getlist('groups[]')

        for playbook in playbook_repository.playbooks:
            if filename in playbook._file_name:
                for play in playbook.get_plays():
                    if playbook_host == play.get_name():
                        if hosts:
                            setattr(play, 'hosts', ','.join(hosts))
                        else:
                            setattr(play, 'hosts', ','.join(groups))

        playbook_repository.salvarPlaybooks()

        return redirect_main(repository.pk)

class AddFileView(CreateView):
    """Class Add File View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        if request.POST['file'] and request.POST['playbook[]']:
            playbooks = request.POST.getlist('playbook[]')
            file = request.POST['file']
            playbook_repository.addPlaybook(file+'.yaml', playbooks)
            playbook_repository.salvarPlaybooks()

        return redirect_main(repository.pk)

class DeleteFileView(DeleteView):
    """Class Deletar File View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def delete(self, request, *args, **kwargs):
        repository = self.get_object()
        file = self.kwargs.get('file')
        
        path = f"{repository.folderRepository()}/{file}"
        
        if os.path.exists(path):
            os.remove(path)
        
        return JsonResponse({"delete": True}, safe=False)
    
class HostDeleteView(DeleteView):
    """Class Deletar Host View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        del_host = playbook_repository.inventoryRepository.inventory.get_host(
            request.GET['del'])

        if del_host:
            playbook_repository.inventoryRepository.get_inventory().remove_host(del_host)
            playbook_repository.inventoryRepository.remove_host_vars_file(
                del_host.name)
            playbook_repository.inventoryRepository.saveInventory()

        request.GET = None

        return redirect_main(repository.pk)


class GroupDeleteView(DeleteView):
    """Class Group Delete View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        del_group = playbook_repository.inventoryRepository.inventory.groups[request.GET['del']]

        if del_group:
            playbook_repository.inventoryRepository.get_inventory().remove_group(del_group.name)
            playbook_repository.inventoryRepository.remove_group_vars_file(
                del_group.name)
            playbook_repository.inventoryRepository.saveInventory()

        request.GET = None

        return redirect_main(repository.pk)


class HostVarsDetailView (DetailView):
    """Class Host Var Detail View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()
        host = request.GET['host']
        vars_host = playbook_repository.inventoryRepository.getHostVars(host)

        html = ''
        for var in vars_host:
            inventory_parameter = InventoryParameter.objects.get(name=var)
            html += '''<div id="{id}_div_parameter" class="input-group">
                        {html}
                      <button class="btn btn-outline-secondary" type="button" onclick="removeInventoryParameter('{id}_div_parameter')"><span class="bi-trash"></span></button>
                      </div>'''.format(id=inventory_parameter.id,
                                       html=getHtmlInventoryParameter(inventory_parameter, vars_host[var]))

        return HttpResponse(html)


class GroupVarsDetailView (DetailView):
    """Class Group Vars Detail View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def get(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()
        request_group = request.GET['group']
        vars_group = playbook_repository.inventoryRepository.getGroupVars(request_group)

        html = ''
        for var in vars_group:
            inventory_parameter = InventoryParameter.objects.get(name=var)
            html += '''<div id="{id}_div_parameter" class="input-group">
                        {html}
                      <button class="btn btn-outline-secondary" type="button" onclick="removeInventoryParameter('{id}_div_parameter')"><span class="bi-trash"></span></button>
                      </div>'''.format(id=inventory_parameter.id, 
                                       html=getHtmlInventoryParameter(inventory_parameter, vars_group[var]))

        return HttpResponse(html)


class AddGroupView(CreateView):
    """Class Add Group View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        params_data = get_params(request.POST.dict())

        group_object = None
        if request.POST['group'] in playbook_repository.inventoryRepository.inventory.groups:
            group_object = playbook_repository.inventoryRepository.inventory.groups[
                request.POST['group']]

        if request.POST['group'] and not group_object:
            group = request.POST['group']
            playbook_repository.inventoryRepository.inventory.add_group(group)
            playbook_repository.inventoryRepository.addVarsGroup(
                group, params_data)
            playbook_repository.inventoryRepository.saveInventory()
        else:
            playbook_repository.inventoryRepository.addVarsGroup(
                group_object.name, params_data)
            playbook_repository.inventoryRepository.saveInventory()

        return redirect_main(repository.pk)


class AddHostView(CreateView):
    """Class Add Host View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        params_data = get_params(request.POST.dict())

        all_file_data = request.FILES.dict()
        for line in all_file_data:
            if line.startswith('param__'):
                params_key = line.replace('param__', '')
                
                path = 'files/'
                if params_key in 'ansible_ssh_private_key_file':
                    path = 'files/keys/'
                
                path_files = playbook_repository.inventoryRepository.repository.folderRepository() +'/'+ path
                handle_uploaded_file(all_file_data[line], path_files)
                params_data[params_key] = path+all_file_data[line].name

        hostObject = playbook_repository.inventoryRepository.inventory.get_host(
            request.POST['host'])

        if request.POST['host'] and not hostObject:
            host = request.POST['host']
            playbook_repository.inventoryRepository.inventory.add_host(
                host, 'all')
            playbook_repository.inventoryRepository.addVarsHost(
                host, params_data)
            playbook_repository.inventoryRepository.saveInventory()
        else:
            playbook_repository.inventoryRepository.addVarsHost(
                hostObject.name, params_data)
            playbook_repository.inventoryRepository.saveInventory()

        return redirect_main(repository.pk)


class JoinGroupHostView(CreateView):
    """Class Join Host in Group View"""
    model = Repository
    template_name = "repository/playbook_form.html"

    def post(self, request, *args, **kwargs):
        repository = self.get_object()
        playbook_repository = repository.getPlaybookRepository()

        groupPost = request.POST.getlist('groups[]')

        if request.POST['hostJoinGroup'] and groupPost:
            host = playbook_repository.inventoryRepository.inventory.get_host(
                request.POST['hostJoinGroup'])

            if host:
                # zerando os grupos
                for g in host.groups:
                    g.remove_host(host)

                host.groups = []

                for group in groupPost:
                    g = playbook_repository.inventoryRepository.inventory.groups[group]
                    g.add_host(host)
                    host.add_group(g)

                playbook_repository.inventoryRepository.saveInventory()

        return redirect_main(repository.pk)
