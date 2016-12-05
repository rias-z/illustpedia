from django.conf.urls import url
from . import views

app_name = 'general'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^login', views.LoginView.as_view(), name="login"),
    url(r'^top', views.TopView.as_view(), name="top"),
]