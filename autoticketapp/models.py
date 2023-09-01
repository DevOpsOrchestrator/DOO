from email.policy import default
from re import template
from django.db import models

from django.contrib.auth.models import User

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

# Class to handle tickets
class Ticket(models.Model):

    numero = models.IntegerField(
        null = True,
    )

    titulo = models.CharField(
        max_length=100,
        verbose_name='Titulo',
    )

    descricao = models.TextField(
        null = True,
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
        null= True,
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
    titulo = models.CharField(
        max_length=100,
        verbose_name='Título',
    )
    
    codigo = models.TextField(
        verbose_name='Código',
    )
    
    service = models.ManyToManyField(
        Service,
        related_name='templates',
    )

    def __str__(self):
        return self.titulo

# Class to handle provision
class provision(models.Model):

    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='provision_ticket',
    )

    template = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='provision_template',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='provisions',
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )



    