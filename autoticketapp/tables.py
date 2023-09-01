import django_tables2 as tables
from django_tables2.utils import Accessor
from django_tables2.columns import TemplateColumn

from .models import Ticket
from .models import Team
from .models import Group
from .models import Template

class BaseTable(tables.Table):
    template_name = "django_tables2/bootstrap.html"

class TicketTable(tables.Table):

    numero = tables.LinkColumn(
        viewname='autoticket:ticket_detail',
        args=[Accessor('id')]
    )

    controls = TemplateColumn(verbose_name=' ', template_name='autoticketapp/ticket_controls.html')

    class Meta:
        model = Ticket
        template_name = "django_tables2/bootstrap4.html"
        fields = ("numero","titulo","descricao","data_inicio","prioridade","controls" )


class TeamTable(tables.Table):

    numero = tables.LinkColumn(
        viewname='autoticket:team_detail',
        args=[Accessor('id')]
    )

    controls = TemplateColumn(verbose_name=' ', template_name='autoticketapp/team_controls.html')

    class Meta:
        model = Team
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nome',)
        
class GroupTable(tables.Table):

    numero = tables.LinkColumn(
        viewname='autoticket:group_detail',
        args=[Accessor('id')]
    )

    controls = TemplateColumn(verbose_name=' ', template_name='autoticketapp/group_controls.html')

    class Meta:
        model = Group
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nome', 'equipe')
        
class ServiceTable(tables.Table):

    numero = tables.LinkColumn(
        viewname='autoticket:service_detail',
        args=[Accessor('id')]
    )

    controls = TemplateColumn(verbose_name=' ', template_name='autoticketapp/service_controls.html')

    class Meta:
        model = Group
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nome', 'status', 'grupo')
        
class TemplateTable(tables.Table):

    # numero = tables.LinkColumn(
    #     viewname='autoticket:template_detail',
    #     args=[Accessor('id')]
    # )

    controls = TemplateColumn(verbose_name=' ', template_name='autoticketapp/template_controls.html')

    class Meta:
        model = Template
        template_name = "django_tables2/bootstrap4.html"
        fields = ('titulo', 'código')
