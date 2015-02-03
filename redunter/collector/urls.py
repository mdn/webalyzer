from django.conf.urls import patterns, include, url

from redunter.collector import views


urlpatterns = patterns('',
    url(r'^$', views.collect, name='collect'),
)
