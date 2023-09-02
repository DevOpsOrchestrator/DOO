from rest_framework.routers import APIRootView
from rest_framework.viewsets import ModelViewSet
from users.querysets import RestrictedQuerySet

from ..models import  Ticket,Team, Group, Service, Template
from . import serializers

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
# Template
#

class TemplateViewSet(ModelViewSet):
    queryset = RestrictedQuerySet(model=Template).all()
    serializer_class = serializers.TemplateSerializer
