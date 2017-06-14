from django.conf.urls import url

from . import views

app_name = 'hisakata'
urlpatterns = [
    url(r'^detail/$', views.yearlist, name='yearlist'),
    url(r'^detail/(?P<year>[0-9]+)/$', views.DateListView.as_view(), name='datelist'),
    url(r'^detail/create/$', views.DateCreateView.as_view(), name='create'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$', views.detailview, name='detail'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/edit/(?P<round_n>[0-9]+)/$', views.formview,
        name='edit'),
    url(r'^detail/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/edit/(?P<round_n>[0-9]+)/create/$',
        views.createformview, name='createround'),
    url(r'^table/$', views.tableyearlist, name='tableyearlist'),
    url(r'^table/(?P<year>[0-9]+)/$', views.MonthListView.as_view(), name='tablelist'),
    url(r'^table/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.tableview, name='table'),
]
