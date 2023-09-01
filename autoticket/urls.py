from django.contrib import admin
from django.urls import path, include, re_path

from autoticketapp.views import HomeView
from .api.views import APIRootView, StatusView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

openapi_info = openapi.Info(
    title="Autoticket API",
    default_version='v1',
    description="API do autoticket",
    terms_of_service="https://github.com/thiagoalima/autoticket",
    license=openapi.License(name="Apache v2 License"),
)

schema_view = get_schema_view(
    openapi_info,
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=()
)

app_name = 'autoticket-api'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('autoticket/', include('autoticketapp.urls')),
    path('autoticket/users', include('users.urls')),
    path('repository/', include('repository.urls')),
    path('iac/', include('iac.urls')),
    path('admin/', admin.site.urls),

     # API
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/auth/', include('rest_framework.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/autoticket/', include('autoticketapp.api.urls')),
    path('api/status/', StatusView.as_view(), name='api-status'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=86400), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=86400), name='api_redocs'),
    re_path(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=86400), name='schema_swagger'),

]
