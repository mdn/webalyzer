from django.conf.urls import patterns, include, url

from redunter.analyzer import views


urlpatterns = patterns('',
    url(r'^$', views.analyze, name='analyze'),
    url(r'^start/$', views.start, name='start'),
    url(
        r'^(?P<domain>[\w\.]+)/source/(?P<id>\d+)/$',
        views.source_view,
        name='source_view'
    ),
    url(r'^(?P<domain>[\w\.]+)$', views.analyzed, name='analyzed'),
)
