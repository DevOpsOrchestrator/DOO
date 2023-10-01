import os
import yaml
from datetime import datetime

from django.db import models

from django.contrib.auth.models import User

from ansible.plugins.loader import init_plugin_loader
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Playbook
from git import Repo

from repository.models import Repository
from repository.dumper import AnsibleDumperRepository
from repository.constants import ATTRIBUTES_PLAYBOOK

PRIORIDADE_EMERGENCIAL = 1
PRIORIDADE_URGENTE = 2
PRIORIDADE_ALTA = 3
PRIORIDADE_MEDIA = 4
PRIORIDADE_BAIXA = 5

PRIORIDADE_CHOICES = [
    (PRIORIDADE_EMERGENCIAL, 'Emergencial'),
    (PRIORIDADE_URGENTE, 'Urgente'),
    (PRIORIDADE_ALTA, 'Alta'),
    (PRIORIDADE_MEDIA, 'Media'),
    (PRIORIDADE_BAIXA, 'Baixa'),
]

STATUS_ATIVO = 1
STATUS_INATIVO = 2

STATUS_CHOICES = (
    (STATUS_ATIVO, "Ativo"),
    (STATUS_INATIVO, "Inativo"),
)

TYPE_INPUT = (
    (1, "Text Short"),
    (2, "Text Long"),
)

# Class to handle tickets


class Ticket(models.Model):

    numero = models.IntegerField(
        null=True,
    )

    titulo = models.CharField(
        max_length=100,
        verbose_name='Titulo',
    )

    descricao = models.TextField(
        null=True,
        max_length=255,
        verbose_name='Descrição',
    )

    prioridade = models.IntegerField(
        choices=PRIORIDADE_CHOICES,
        default=PRIORIDADE_MEDIA,
    )

    data_inicio = models.DateTimeField(
        auto_now_add=True,
    )

    data_fim = models.DateTimeField(
        null=True,
    )

#  Class to handle teams


class Team(models.Model):
    # Uma equipe pode ter vários grupos
    nome = models.CharField(
        max_length=50,
        verbose_name='Equipe',
        null=True,
    )

    def __str__(self):
        return self.nome

#  Class to handle groups


class Group(models.Model):
    # Um grupo pode ter vários serviços e estar em apenas uma equipe
    nome = models.CharField(
        max_length=50,
        verbose_name='Grupo',
        null=True,
    )

    equipe = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='groups',
    )

    def __str__(self):
        return self.nome

# Class to handle services


class Service(models.Model):
    # Um serviço pode ter vários templates e estar em um único grupo
    nome = models.CharField(
        max_length=50,
        verbose_name='Serviço',
        null=True,
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_ATIVO,
    )

    grupo = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='services',
    )

    def __str__(self):
        return self.nome

# Class to handle templates


class Template(models.Model):
    # Um template pode ser usado por vários serviços
    def __init__(self, *args, **kwargs):
        self.playbook = None
        super().__init__(*args, **kwargs)

    name = models.CharField(
        max_length=100,
        verbose_name='Name',
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    filename = models.CharField(
        null=True,
    )

    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name='templates', null=True)

    def __str__(self):
        return self.name

    def retirar_nulos(self, data, listAtrribute=None):
        if listAtrribute:
            return {k: v for k, v in data.items() if v and k in listAtrribute}
        return {k: v for k, v in data.items() if v}
    
    def get_path_playbook(self):
        return f'{self.repository.folderRepository()}/templates/{self.filename}.yml'
    
    def commitAndPush(self):
        dataAtual= datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        #TODO coloca o usuario que fez o commit
        commit_message = f'commit realizado em {dataAtual}'

        repo = Repo(self.repository.folderRepository())

        #TODO fazer pull

        repo.git.add('--all')
        repo.index.commit(commit_message)

        origin = repo.remote(name='origin')
        origin.push()

    def get_playbook(self):
        loader = DataLoader()

        init_plugin_loader([])

        playbook_path = self.get_path_playbook()

        if os.path.exists(playbook_path):
            self.playbook = Playbook.load(playbook_path, loader=loader)

        return self.playbook

    def salvarPlaybook(self):

        dataPlaybook = []
        for p in self.playbook._entries:
            validos = self.retirar_nulos(p.serialize(), ATTRIBUTES_PLAYBOOK)

            data = {'name': validos.pop('name')}
            data.update(validos)

            dataPlaybook.append(data)

        self.salvarYaml(dataPlaybook, filename=self.filename+'.yml')
        self.commitAndPush()

    def salvarYaml(self, data, folder=None, filename=None):
        if not filename:
            filename = 'main.yml'
        if not folder:
            folder = self.repository.folderRepository()

        with open(folder+'/templates/'+filename, 'w') as file:
            documents = yaml.dump(data, file, Dumper=AnsibleDumperRepository, explicit_start=True, explicit_end=True,
                                  sort_keys=False, default_flow_style=False, default_style='', allow_unicode=True)


# Class to handle provision
class Provision(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='provision_ticket',
    )

    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='provision_template',
    )
    
    prompt = models.TextField(null=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='provisions',
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )
    
    def __str__(self):
        return f"{self.template.name} ({self.date.strftime('%d/%m/%Y %H:%M:%S')})"
