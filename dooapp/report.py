from dataclasses import dataclass

from rest_framework import serializers
from django.db.models import Count
from .models import Group, Service, Team

@dataclass
class ReportEntry:
    team: Team
    group_count: int
    service_count: int
    template_count: int

def team_report():
    """
        Generate team report
    """
    data = []
    
    querySet = Team.objects.values("nome").annotate(
        group_count=Team.objects.values('groups').distinct(),       # substituir "Group" por query que busca os grupos da equipe
        service_count=Group.objects.values('services').distinct(),    # substituir "Service" por query que busca os serviços do grupo
        template_count=Service.objects.values('templates').distinct(),   # substituir "Template" por query que busca os templates do grupo
    )
    
    team_index = {}
    for team in Team.objects.all():
        team_index[team.pk] = team
    
    for entry in querySet:
        team = team_index.get(entry['nome'])
        report_entry = ReportEntry(
            team=team,
            group_count=entry['group_count'],
            service_count=entry['service_count'],
            template_count=entry['template_count']
        )

        data.append(report_entry)
        
    return data

class TeamSerializer(serializers.ModelSerializer):
    """
        Serialization of the team model
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Team
        fields = ("id", "nome")
    
class ReportSerializer(serializers.Serializer):
    """
        Serialization of team report data
    """
    team = TeamSerializer()
    group_count = serializers.IntegerField()
    service_count = serializers.IntegerField()
    template_count = serializers.IntegerField()