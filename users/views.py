import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View


from django.views.generic.edit import CreateView,UpdateView, DeleteView, FormView

from .models import Token

from .forms import TokenForm

SUCCESS_URL ='/autoticket/usersapi-tokens/'

#
# Login/logout
#

class LoginView(View):
    """
    Perform user authentication via the web UI.
    """
    template_name = 'users/login.html'

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = AuthenticationForm(request)

        if request.user.is_authenticated:
            logger = logging.getLogger('users.auth.login')
            return self.redirect_to_next(request, logger)

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        logger = logging.getLogger('users.auth.login')
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            logger.debug("Login form validation was successful")

            # Authenticate user
            auth_login(request, form.get_user())
            logger.info(f"Usuario {request.user} autenticado com sucesso")
            messages.info(request, f"Logado como {request.user}.")

            return self.redirect_to_next(request, logger)

        else:
            logger.debug("Login form validation failed")

        return render(request, self.template_name, {
            'form': form,
        })

    def redirect_to_next(self, request, logger):
        data = request.POST if request.method == "POST" else request.GET
        redirect_url = data.get('next', settings.LOGIN_REDIRECT_URL)

        if redirect_url and url_has_allowed_host_and_scheme(redirect_url, allowed_hosts=None):
            logger.debug(f"Redirecionando o usuario para {redirect_url}")
        else:
            if redirect_url:
                logger.warning(f"Ignorando 'next' URL passado para o form login: {redirect_url}")
            redirect_url = reverse('home')

        return HttpResponseRedirect(redirect_url)


class LogoutView(View):

    def get(self, request):

        # Log out the user
        username = request.user
        auth_logout(request)
  
        messages.info(request, "Você foi deslogado.")

        # Delete session key cookie (if set) upon logout
        response = HttpResponseRedirect(reverse('autoticket:home'))
        response.delete_cookie('session_key')

        return response


#
# User profiles
#

class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'users/password.html'

    def get(self, request):

        form = DjangoPasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        form = DjangoPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Seu password foi alterado com sucesso.")
            return redirect('home')

        return render(request, self.template_name, {
            'form': form,
        })


#
# API tokens
#

class TokenListView(LoginRequiredMixin, View):

    def get(self, request):

        tokens = Token.objects.filter(user=request.user)

        return render(request, 'users/api_tokens.html', {
            'tokens': tokens,
            'active_tab': 'api-tokens',
        })

class TokenCreateView(LoginRequiredMixin, FormView):
    form_class = TokenForm
    success_url = SUCCESS_URL
    template_name = "users/token_form.html"

    def form_valid(self, form):
        token = form.save(commit=False)
        token.user = self.request.user
        token.save()

        msg = f"Token criado"
        messages.success(self.request, msg)

        return super().form_valid(form)

class TokenUpdateView(LoginRequiredMixin, UpdateView):
    model = Token
    fields = ["key","write_enabled","expires","description"]
    success_url = SUCCESS_URL
    template_name = "users/token_form.html"

class TokenDeleteView(LoginRequiredMixin, DeleteView):
    model = Token
    success_url = SUCCESS_URL
    template_name = "users/confirm_delete.html"