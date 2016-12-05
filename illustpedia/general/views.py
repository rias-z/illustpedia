from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect


class IndexView(generic.TemplateView):
    template_name = 'I000_index.html'


class LoginView(generic.FormView):
    template_name = 'I001_login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('general:top')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(user=user, request=self.request)
        return super(LoginView, self).form_valid(form)


class LogoutView(generic.View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('general:login')


class AccountCreateView(generic.TemplateView):
    template_name = 'I002_account_create.html'

class TopView(generic.TemplateView):
    template_name = 'I003_top.html'


class AccountView(generic.TemplateView):
    template_name = 'I004_account.html'


class ArtistDetailView(generic.TemplateView):
    template_name = 'I005_artist_detail.html'
