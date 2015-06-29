import re
from django.conf.urls import patterns, url

from webalyzer.collector import views

urlpatterns = patterns(
    '',
    url(
        re.compile('^check/(?P<source_type>[\w]+)/'
                   '(?P<domain>[\w\.]+)/'
                   '(?P<source_hash>[\-\w\.]+)$'),
        views.collect_check,
        name='collect_check'
    ),
    url(r'^$', views.collect, name='collect'),
)
