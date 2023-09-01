from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField,RelatedField

from users.models import ObjectPermission, Token
from .nested_serializers import *


__all__ = (
    'GroupSerializer',
    'ObjectPermissionSerializer',
    'TokenSerializer',
    'UserSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:user-detail')
    groups = PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        many=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
            'date_joined', 'groups',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Extract the password from validated data and set it separately to ensure proper hash generation.
        """
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user

    def get_display(self, obj):
        if full_name := obj.get_full_name():
            return f"{obj.username} ({full_name})"
        return obj.username


class GroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:group-detail')
    user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'url', 'name', 'user_count')


class TokenSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:token-detail')
    key = serializers.CharField(min_length=40, max_length=40, allow_blank=True, required=False)
    user = NestedUserSerializer()

    class Meta:
        model = Token
        fields = ('id', 'url', 'user', 'created', 'expires', 'key', 'write_enabled', 'description')

    def to_internal_value(self, data):
        if 'key' not in data:
            data['key'] = Token.generate_key()
        return super().to_internal_value(data)


class TokenProvisionSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ObjectPermissionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-api:objectpermission-detail')
    object_types = RelatedField(
        queryset=ContentType.objects.all(),
        many=True
    )
    groups = PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        many=True
    )
    users = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        many=True
    )

    class Meta:
        model = ObjectPermission
        fields = (
            'id', 'url', 'name', 'description', 'enabled', 'object_types', 'groups', 'users', 'actions',
            'constraints',
        )
