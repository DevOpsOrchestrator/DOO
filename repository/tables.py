import django_tables2 as tables
from django_tables2.utils import Accessor
from django_tables2.columns import TemplateColumn

from .models import (
    Repository
)

class BaseTable(tables.Table):
    template_name = "django_tables2/bootstrap.html"

class RepositoryTable(tables.Table):

    id = tables.LinkColumn(
        viewname='repository:repo_detail',
        args=[Accessor('id')]
    )

    controls = TemplateColumn(verbose_name=' ', template_name='repository/repo_controls.html')

    class Meta:
        model = Repository
        template_name = "django_tables2/bootstrap5-responsive.html"
        fields = ("id","nome","url","token","token_key" )
        attrs = {'class': 'table table-striped'}