from rest_framework import serializers

from ..models import Ticket,Team,Group,Service,Template,FormItens


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = '__all__'

class GroupTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = '__all__'

class TemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = '__all__'

class FormItensSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormItens
        fields = '__all__'


    
