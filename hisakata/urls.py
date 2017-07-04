from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'hisakata'
urlpatterns = [
    url(r'^detail/$', views.yearlist, name='yearlist'),
    url(r'^detail/(?P<year>[0-9]+)/$', views.monthlistview, name='monthlist'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.datelistview, name='datelist'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/create/$', views.datecreateview, name='create'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$', views.detailview, name='detail'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/edit/(?P<round_n>[0-9]+-*[0-9]*)/$',
        views.formview,
        name='edit'),
    url(r'^table/$', views.tableyearlist, name='tableyearlist'),
    url(r'^table/(?P<year>[0-9]+)/$', views.tablemonthlist, name='tablelist'),
    url(r'^table/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<grade>[0-9]+)/$', views.tableview, name='table'),
    url(r'^player/(?P<grade>[0-9]*)$', views.playerview, name='player'),
    url(r'^$', views.homeview, name='homeview'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'hisakata/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'template_name': 'hisakata/logged_out.html'}, name='logout'),
    url(r'^delete/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$', views.deletemodel, name='delete'),
]
