from django.urls import path
from .views import InventoryParameterHTML, playbookParameterHTML, ansibleModuleVariableHTML

app_name = 'iac'

urlpatterns = [
    path('inventoryParameter/<str:parametro>/', InventoryParameterHTML, name='InventoryParameter_detail_html'),
    path('playbookParameter/<str:parametro>/', playbookParameterHTML, name='PlaybookParameter_detail_html'),
    path('ansibleModuleVariable/<str:parametro>/', ansibleModuleVariableHTML, name='AnsibleModuleVariable_detail_html'),
]