from django.conf.urls import url
from . import views

app_name = 'general'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^account_create/$', views.AccountCreateView.as_view(), name="account_create"),
    url(r'^top/$', views.TopView.as_view(), name="top"),
    url(r'^account/$', views.AccountView.as_view(), name="account"),
    url(r'^artist_detail/(?P<pk>[0-9]+)/$', views.ArtistDetailView.as_view(), name="artist_detail"),
    url(r'^artist_create/$', views.ArtistCreateView.as_view(), name="artist_create"),
    # url(r'^tag_search/(?P<pk>[0-9]+)/$', views.TagSearchView.as_view(), name="tag_search"),
    url(r'^tag_search/tag=(?P<tag_list>[\w,]+)/$', views.TagSearchView.as_view(), name="tag_search"),
    url(r'^auto_create/$', views.ArtistAutoCreateView.as_view(), name="auto_create"),
]
