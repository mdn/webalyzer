from django.conf.urls import patterns, url

from webalyzer.analyzer import views


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^submit/$', views.submit, name='submit'),
    url(
        r'^recent-submissions$',
        views.recent_submissions,
        name='recent_submissions'
    ),
    url(r'^(?P<domain>[\w\.]+)$', views.index, name='analyzed'),
    url(r'^(?P<domain>[\w\.]+)/data$', views.analyzed, name='analyzed_data'),
    url(
        r'^(?P<domain>[\w\.]+)/source/(?P<id>\d+)/$',
        views.index,
        name='source_view'
    ),
    url(
        r'^(?P<domain>[\w\.]+)/source/(?P<id>\d+)/data$',
        views.source_view,
        name='source_view_data'
    ),
    url(
        r'^(?P<domain>[\w\.]+)/download/(?P<id>\d+)/'
        '(?P<which>before|after)/(?P<filename>.*?\.css)$',
        views.download,
        name='download'
    ),
    # url(r'^$', views.analyze, name='analyze'),
    # url(r'^start/$', views.start, name='start'),
    # url(
    #     r'^(?P<domain>[\w\.]+)/source/(?P<id>\d+)/$',
    #     views.source_view,
    #     name='source_view'
    # ),
    # url(
    #     r'^(?P<domain>[\w\.]+)/diff/(?P<id>\d+)/$',
    #     views.diff_view,
    #     name='diff_view'
    # ),
    # url(r'^(?P<domain>[\w\.]+)$', views.analyzed, name='analyzed'),

)
