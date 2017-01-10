from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'general'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="home"),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    url(r'^account_create/$', views.AccountCreateView.as_view(), name="account_create"),
    url(r'^top/$', views.TopView.as_view(), name="top"),
    url(r'^account/$', views.AccountView.as_view(), name="account"),
    url(r'^artist_detail/(?P<pk>[0-9]+)/$', views.ArtistDetailView.as_view(), name="artist_detail"),
    url(r'^artist_update/(?P<pk>[0-9]+)/$', views.ArtistUpdateView.as_view(), name="artist_update"),
    url(r'^artist_create/$', views.ArtistCreateView.as_view(), name="artist_create"),
    url(r'^tag_search/tag_list=(?P<tag_list>[\w,]+)/is_all=(?P<is_all>[\d,]+)/$',
        views.TagSearchView.as_view(), name="tag_search"),
    url(r'^tag_search_from_artist/tag_num=(?P<tag_num>[\d,]+)/$',
        views.TagSearchFromArtistView.as_view(), name="tag_search_from_artist"),
    url(r'^auto_create_from_ranking/$', views.ArtistAutoCreateFromRankingView.as_view(), name="auto_create_from_ranking"),
    url(r'^auto_create_from_follow/$', views.ArtistAutoCreateFromFollowView.as_view(), name="auto_create_from_follow"),
    url(r'^all_artist/$', views.AllArtistView.as_view(), name="all_artist"),
    url(r'^server_admin/$', views.ServerAdminView.as_view(), name="server_admin"),

    url(r'^illust_top/$', views.IllustDBTopView.as_view(), name="illust_top"),
    url(r'^illust_register/$', views.IllustDBRegisterView.as_view(), name="illust_register"),
    url(r'^illust_detail/(?P<pk>[0-9]+)/$', views.IllustDBDetailView.as_view(), name="illust_detail"),
    url(r'^illust_tag_search/tag_list=(?P<tag_list>[\w,]+)/$', views.IllustTagSearchView.as_view(),
        name="illust_tag_search"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
