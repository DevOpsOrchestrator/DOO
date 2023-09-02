from django.contrib import admin
from django.urls import path, include, re_path

from dooapp.views import HomeView
from .api.views import APIRootView, StatusView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

openapi_info = openapi.Info(
    title="doo API",
    default_version='v1',
    description="API do doo",
    terms_of_service="https://github.com/thiagoalima/doo",
    license=openapi.License(name="Apache v2 License"),
)

schema_view = get_schema_view(
    openapi_info,
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=()
)

app_name = 'doo-api'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('doo/', include('dooapp.urls')),
    path('doo/users', include('users.urls')),
    path('repository/', include('repository.urls')),
    path('iac/', include('iac.urls')),
    path('admin/', admin.site.urls),

     # API
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/auth/', include('rest_framework.urls')),
    path('api/users/', include('users.api.urls')),
    path('api/doo/', include('dooapp.api.urls')),
    path('api/status/', StatusView.as_view(), name='api-status'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=86400), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=86400), name='api_redocs'),
    re_path(r'^api/swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=86400), name='schema_swagger'),

]
