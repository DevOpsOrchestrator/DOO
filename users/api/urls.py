from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.APIRootView = views.UsersRootView

# Users and groups
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)

# Tokens
router.register('tokens', views.TokenViewSet)

# Permissions
router.register('permissions', views.ObjectPermissionViewSet)

app_name = 'users-api'
urlpatterns = [
    path('tokens/provision/', views.TokenProvisionView.as_view(), name='token_provision'),
    path('', include(router.urls)),
]
