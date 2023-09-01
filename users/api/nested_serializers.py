from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from rest_framework import serializers
from rest_framework.relations import RelatedField

from users.models import ObjectPermission, Token

__all__ = [
    'NestedGroupSerializer',
    'NestedObjectPermissionSerializer',
    'NestedTokenSerializer',
    'NestedUserSerializer',
]


class NestedGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:group-detail')

    class Meta:
        model = Group
        fields = ['id', 'url', 'name']


class NestedUserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:user-detail')

    class Meta:
        model = User
        fields = ['id', 'url', 'username']

    def get_display(self, obj):
        if full_name := obj.get_full_name():
            return f"{obj.username} ({full_name})"
        return obj.username


class NestedTokenSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:token-detail')

    class Meta:
        model = Token
        fields = ['id', 'url', 'key', 'write_enabled']


class NestedObjectPermissionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:objectpermission-detail')
    object_types = RelatedField(
        queryset=ContentType.objects.all(),
        many=True
    )
    groups = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ObjectPermission
        fields = ['id', 'url', 'name', 'enabled', 'object_types', 'groups', 'users', 'actions']

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_users(self, obj):
        return [u.username for u in obj.users.all()]
