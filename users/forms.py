
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms

from .models import Token

class TokenForm(LoginRequiredMixin, forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="Se nenhuma chave for fornecida, uma será gerada automaticamente."
    )

    class Meta:
        model = Token
        fields = [
            'key', 'write_enabled', 'expires', 'description',
        ]

class ReturnURLForm(forms.Form):
    """
    Fornece um campo de URL de retorno oculto para controlar para onde o usuário é direcionado após o envio do formulário.
    """
    return_url = forms.CharField(required=False, widget=forms.HiddenInput())


class ConfirmationForm(ReturnURLForm):
    """
   Um formulário de confirmação genérico. O formulário não é válido a menos que o campo de confirmação esteja marcado.
    """
    confirm = forms.BooleanField(required=True, widget=forms.HiddenInput(), initial=True)