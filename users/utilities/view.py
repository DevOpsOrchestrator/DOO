from users.permissions import get_permission_for_model
from django.views.generic.edit import CreateView,UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_tables2 import SingleTableView

DEFAULT_URL_SUCCESS = "/autoticket/ticket/"

class BaseView(PermissionRequiredMixin):
    
    def has_permission(self):
        user = self.request.user
        permission_required = self.get_required_permission()

        # Checa se o usuario tem a permissão solicitada
        if user.has_perm(perm=permission_required):
            return True

        return False

class DetailView(BaseView, DetailView):

    def get_required_permission(self):
        return get_permission_for_model(self.model, 'view')

class TableView(BaseView,SingleTableView):
    paginate_by = 10

    def get_required_permission(self):
        return get_permission_for_model(self.model, 'view')

class CreateView(BaseView, CreateView):
    success_url = DEFAULT_URL_SUCCESS

    def get_required_permission(self):
        return get_permission_for_model(self.model, 'add')

class UpdateView(BaseView, UpdateView):
    success_url = DEFAULT_URL_SUCCESS

    def get_required_permission(self):
        return get_permission_for_model(self.model, 'change')

class DeleteView(BaseView, DeleteView):
    success_url = DEFAULT_URL_SUCCESS

    def get_required_permission(self):
        return get_permission_for_model(self.model, 'delete')