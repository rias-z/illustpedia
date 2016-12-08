from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import IPUser, Artist


# form
class AccountCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = IPUser
        fields = ("username", "nickname", "email")


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


class AccountCreateView(generic.CreateView):
    template_name = 'I002_account_create.html'
    form_class = AccountCreateForm
    success_url = reverse_lazy('general:top')

    def done(self, request, cleaned_data):
        obj = AccountCreateForm(request.POST).save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        # user = authenticate(username=cleaned_data['username'],
        #                     password=cleaned_data['password1'])
        # login(self.request, user)
        # return redirect(reverse('general:top', args=(), kwargs={}))

    def get_success_url(self):
            return reverse_lazy('general:login')


class TopView(generic.TemplateView):
    template_name = 'I003_top.html'

    def get_context_data(self, **kwargs):
        context = super(TopView, self).get_context_data(**kwargs)
        context['artist_list'] = Artist.objects.all()
        return context


class AccountView(generic.TemplateView):
    template_name = 'I004_account.html'


class ArtistDetailView(generic.DetailView):
    template_name = 'I006_artist_detail.html'
    model = Artist

    def get_queryset(self):
        self.queryset = Artist.objects.all()
        return super(ArtistDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['artist'] = self.get_object()
        context['tag_list'] = self.get_object().tags.all()
        return context

