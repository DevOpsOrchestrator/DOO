import platform
from collections import OrderedDict

from django import __version__ as DJANGO_VERSION
from django.apps import apps
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


from users.api.authentication import IsAuthenticatedOrLoginNotRequired


class APIRootView(APIView):
    """
    Esta é a raiza do doo REST API.
    """
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

    def get_view_name(self):
        return "API Root"

    def get(self, request, format=None):

        return Response(OrderedDict((
            ('users', reverse('users-api:api-root', request=request, format=format)),
            ('doo', reverse('doo-api:api-root', request=request, format=format)),
            ('login',  reverse('rest_framework:login', request=request, format=format)),
            ('logout',  reverse('rest_framework:logout', request=request, format=format)),
        )))


class StatusView(APIView):
    """
    A lightweight read-only endpoint for conveying NetBox's current operational status.
    """
    permission_classes = [IsAuthenticatedOrLoginNotRequired]

    def get(self, request):
        # Gather the version numbers from all installed Django apps
        installed_apps = {}
        for app_config in apps.get_app_configs():
            app = app_config.module
            version = getattr(app, 'VERSION', getattr(app, '__version__', None))
            if version:
                if type(version) is tuple:
                    version = '.'.join(str(n) for n in version)
                installed_apps[app_config.name] = version
        installed_apps = {k: v for k, v in sorted(installed_apps.items())}

        return Response({
            'django-version': DJANGO_VERSION,
            'installed-apps': installed_apps,
            'python-version': platform.python_version(),
        })
