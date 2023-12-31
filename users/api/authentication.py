from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.permissions import BasePermission, DjangoObjectPermissions, SAFE_METHODS

from users.models import Token

LOGIN_REQUIRED = True


class TokenAuthentication(authentication.TokenAuthentication):
    """
    A custom authentication scheme which enforces Token expiration times.
    """
    model = Token

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.prefetch_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")

        # Enforce the Token's expiration time, if one has been set.
        if token.is_expired:
            raise exceptions.AuthenticationFailed("Token expired")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")

        return token.user, token


class TokenPermissions(DjangoObjectPermissions):
    """
    Custom permissions handler which extends the built-in DjangoModelPermissions to validate a Token's write ability
    for unsafe requests (POST/PUT/PATCH/DELETE).
    """
    # Override the stock perm_map to enforce view permissions
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def __init__(self):

        # LOGIN_REQUIRED determines whether read-only access is provided to anonymous users.
        self.authenticated_users_only = LOGIN_REQUIRED

        super().__init__()

    def _verify_write_permission(self, request):

        # If token authentication is in use, verify that the token allows write operations (for unsafe methods).
        if request.method in SAFE_METHODS or request.auth.write_enabled:
            return True

    def has_permission(self, request, view):

        # Enforce Token write ability
        if isinstance(request.auth, Token) and not self._verify_write_permission(request):
            return False

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):

        # Enforce Token write ability
        if isinstance(request.auth, Token) and not self._verify_write_permission(request):
            return False

        return super().has_object_permission(request, view, obj)


class IsAuthenticatedOrLoginNotRequired(BasePermission):
    """
    Returns True if the user is authenticated or LOGIN_REQUIRED is False.
    """
    def has_permission(self, request, view):
        if LOGIN_REQUIRED:
            return True
        return request.user.is_authenticated
