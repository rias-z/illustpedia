from django.views import generic

class IndexView(generic.TemplateView):
    template_name = 'index.html'

class LoginView(generic.TemplateView):
    template_name = 'I001_login.html'

class TopView(generic.TemplateView):
    template_name = 'I002_top.html'