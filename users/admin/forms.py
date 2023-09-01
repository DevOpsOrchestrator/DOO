from django import forms
from django.contrib.auth.models import Group, User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.db.models import Q

from users.constants import OBJECTPERMISSION_OBJECT_TYPES
from users.models import ObjectPermission, Token

__all__ = (
    'GroupAdminForm',
    'ObjectPermissionForm',
    'TokenAdminForm',
)


class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    class Meta:
        model = Group
        fields = ('name', 'users')

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()

        return instance


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="Se nenhuma chave for fornecida, uma será gerada automaticamente."
    )

    class Meta:
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description'
        ]
        model = Token


class ObjectPermissionForm(forms.ModelForm):
    object_types = forms.ModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES
    )
    
    can_view = forms.BooleanField(required=False)
    can_add = forms.BooleanField(required=False)
    can_change = forms.BooleanField(required=False)
    can_delete = forms.BooleanField(required=False)

    class Meta:
        model = ObjectPermission
        exclude = []
        help_texts = {
            'actions': 'Ações concedidas além das listadas acima',
            'constraints': 'Expressão JSON de um filtro de conjunto de consultas que retornará apenas objetos permitidos. Deixar nulo '
                            'para corresponder a todos os objetos deste tipo. Uma lista de vários objetos resultará em um OR lógico '
                            'Operação.'
        }
        labels = {
            'actions': 'Ações adicionais'
        }
        widgets = {
            'constraints': forms.Textarea(attrs={'class': 'vLargeTextField'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Torne o campo de ações opcional, pois o formulário de administração o usa apenas para ações não CRUD
        self.fields['actions'].required = False

        # Order group e campos de usuario
        self.fields['groups'].queryset = self.fields['groups'].queryset.order_by('name')
        self.fields['users'].queryset = self.fields['users'].queryset.order_by('username')

        # Marque as caixas de seleção apropriadas ao editar um ObjectPermission existente
        if self.instance.pk:
            for action in ['view', 'add', 'change', 'delete']:
                if action in self.instance.actions:
                    self.fields[f'can_{action}'].initial = True
                    self.instance.actions.remove(action)

    def clean(self):
        super().clean()

        object_types = self.cleaned_data.get('object_types')
        constraints = self.cleaned_data.get('constraints')

        # Anexe qualquer uma das caixas de seleção CRUD selecionadas à lista de ações
        if not self.cleaned_data.get('actions'):
            self.cleaned_data['actions'] = list()
        for action in ['view', 'add', 'change', 'delete']:
            if self.cleaned_data[f'can_{action}'] and action not in self.cleaned_data['actions']:
                self.cleaned_data['actions'].append(action)

        # Pelo menos uma ação deve ser especificada
        if not self.cleaned_data['actions']:
            raise ValidationError("At least one action must be selected.")

        # Valide as restrições de modelo especificadas tentando executar uma consulta. Não nos importamos se a consulta
         # retorna qualquer coisa; queremos apenas garantir que as restrições especificadas sejam válidas.
        if object_types and constraints:
            # Normaliza as restrições para uma lista de dicts
            if type(constraints) is not list:
                constraints = [constraints]
            for ct in object_types:
                model = ct.model_class()
                try:
                    model.objects.filter(*[Q(**c) for c in constraints]).exists()
                except FieldError as e:
                    raise ValidationError({
                        'constraints': f'Filtro invalido para {model}: {e}'
                    })
