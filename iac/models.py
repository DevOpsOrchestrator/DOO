from django.db import models
import os
import yaml

class AnsibleModule(models.Model): 

    name = models.CharField(
        max_length=200,
        verbose_name='name',
        blank=True
    )

    collection = models.CharField(
        max_length=200,
        verbose_name='collection',
        blank=True
    )

    description = models.CharField(
        max_length=200,
        verbose_name='description',
        null=True,
        blank=True
    )

class AnsibleModuleVariable (models.Model):

    module = models.ForeignKey(
        AnsibleModule,
        on_delete=models.CASCADE,
        related_name='ansible_modules',
        blank=True
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='name',
        blank=False
    )
    
    description = models.TextField(
        verbose_name='description',
         null=True,
         blank=True
    )
    
    variable_type = models.CharField(
        max_length=200,
        verbose_name='type',
        null=True,
        blank=True
    )
    
    choices = models.CharField(
        max_length=255,
        verbose_name='choices',
        null=True,
        blank=True
    )
    
    required = models.BooleanField(
        default=False
    )

class TypeInput(models.Model):

    type = models.CharField(
        max_length=100,
        verbose_name='type',
    )


class InventoryParameter(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name='name',
    )

    description = models.TextField(
        verbose_name='description',
        null=True,
        blank=True
    )

    type = models.ForeignKey(
        TypeInput,
        on_delete=models.CASCADE,
        related_name='inventoryParameters',
    )

    value = models.TextField(
        verbose_name='value',
         null=True,
         blank=True
    )

class PlaybookParameter(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name='name',
    )

    description = models.TextField(
        verbose_name='description',
        null=True,
        blank=True
    )

    type = models.ForeignKey(
        TypeInput,
        on_delete=models.CASCADE,
        related_name='playbookParameters',
    )

    value = models.TextField(
        verbose_name='value',
         null=True,
         blank=True
    )
     

class Host():

    def __init__(self,value):
        self.value = value
        self.variables = []


class Group():

    def __init__(self,name):
        self.name = name
        self.hosts = []
        self.variables = []
        self.groups = []
    
class Inventory():

    def __init__(self,name):
        self.name = name
        self.hosts = []
        self.groups = []

class Module():

    def __init__(self,name,attributes=None):
        self.name = name
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes

class Task():
    ATTRIBUTES = ['action','any_errors_fatal','args','async','become','become_exe','become_flags','become_method','become_user','changed_when','check_mode','collections','connection','debugger','delay','delegate_facts','delegate_to','diff','environment','failed_when','ignore_errors','ignore_unreachable','local_action','loop','loop_control','module_defaults','no_log','poll','port','register','remote_user','retries','run_once','tags','throttle','timeout','until']
    
    def __init__(self,name=None, module=None, handler=None, when=None):
        self.name = name
        self.module = module
        self.variables = None
        self.notify = handler
        self.when = when
        self.attributes = {}
        self.lookups = {}
    
    def deserialize(self, data):
        for key, value in data.items():
            if "name" in key:
                self.name = value
            elif "vars" in key:
                self.variables = value
            elif "notify" in key:
                self.notify = value
            elif "with_" in key:
                self.lookups[key]=value
            elif key in self.ATTRIBUTES:
                self.attributes[key]=value
            else:
                self.module = Module(name=key,attributes=value)

class Handler():

    def __init__(self,name=None, module=None):
        self.name = name
        self.module = module

    def deserialize(self, data):
        for key, value in data.items():
            if key in 'name':
                self.name = value
            else:
                self.module = Module(name=key,attributes=value)
        

class Role():

    def __init__(self,name=None,folder=None):
        self.folder = folder
        self.name = name
        self.vars = []
        self.tasks = []
        self.defaults = []
        self.files = []
        self.handlers = []
        self.templates = []
        self.meta = []
    
    def deserialize(self, data):
        self.name = data
        load = LoadPlaybook(self.folder)
        load.loadRole(self)


""" class Playbook():

    def __init__(self,name=None, hosts=None, folder=None):
        self.folder = folder
        self.name = name
        self.hosts = hosts
        self.attributes = []
        self.roles = []
        self.variables = []
        self.handlers = []
        self.tasks = []

    def deserialize(self, data):
        for key, value in data.items():
            if "name" in key:
                self.name = value
            elif "hosts" in key:
                self.hosts = value
            elif "vars" in key:
                self.variables = value
            elif "roles" in key:
                for r in value:
                    role = Role(name=r,folder=self.folder)
                    role.deserialize(r)
                    self.roles.append(role)
            elif "tasks" in key:
                for t in value:
                    task = Task()
                    task.deserialize(t)
                    self.tasks.append(task)
            elif "handlers" in key:
                for h in value:
                    handler = Handler()
                    handler.deserialize(h)
                    self.handlers.append(handler)
            else: 
                self.attributes[key]=value """

class PlaybookFile():

    def __init__(self,name, folder):
        self.name = name
        self.folder = folder
        self.playbooks = []
        self.loader = LoadPlaybook(folder)

    def deserialize(self, data):
        for p in data:
            playbook = Playbook(folder=self.folder)
            playbook.deserialize(p)
            self.playbooks.append(playbook)

class LoadPlaybook():

    def __init__(self, folder):
        self.folder = folder
    
    def loadPlaybookFiles(self):
        playbookFiles = []

        for play in os.listdir(self.folder): 
            if play.endswith(".yml") or play.endswith(".yaml") :
                with open(self.folder+'/'+play) as file:
                    playbookYaml = yaml.full_load(file)

                    playbookFile = PlaybookFile(name=play,folder=self.folder)                  
                    playbookFile.deserialize(playbookYaml)

                    playbookFiles.append(playbookFile)

        return playbookFiles
    
    def loadRole(self,role):
        role.defaults = self.loadDefaults(role)
        role.files = self.loadFiles(role)
        role.handlers = self.loadHandlers(role)
        role.templates = self.loadTemplates(role)
        role.vars = self.loadVars(role)
        role.meta = self.loadMeta(role)
        role.tasks = self.loadTasks(role)

        return role

    def loadTasks(self,role):
        tasks = []
        with open(self.folder+'/roles/'+role.name+'/tasks/main.yml') as file:
            for t in yaml.full_load(file):
                task = Task()
                task.deserialize(t)
                tasks.append(t)
        return tasks

    def loadMeta(self,role):
        with open(self.folder+'/roles/'+role.name+'/meta/main.yml') as file:
            return yaml.full_load(file)

    def loadVars(self,role):
        with open(self.folder+'/roles/'+role.name+'/vars/main.yml') as file:
            return yaml.full_load(file)

    def loadTemplates(self,role):
        return os.listdir(self.folder+'/roles/'+role.name+'/templates')
    
    def loadHandlers(self,role):
        handlers = []
        with open(self.folder+'/roles/'+role.name+'/handlers/main.yml') as file:
            for h in yaml.full_load(file):
                handler = Handler()
                handler.deserialize(h)
                handlers.append(handler)
        return handlers

    def loadDefaults(self,role):
        with open(self.folder+'/roles/'+role.name+'/defaults/main.yml') as file:
            return yaml.full_load(file)

    def loadFiles(self,role):
        return os.listdir(self.folder+'/roles/'+role.name+'/files')

    def loadInventory(self):
        print(self.repository.folderRepository())
        print(os.listdir(self.repository.folderRepository()))
        print(filter(os.path.isfile, os.listdir(self.repository.folderRepository())))


