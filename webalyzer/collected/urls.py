from django.conf.urls import patterns, url

from webalyzer.collected import views


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(
        r'^(?P<domain>[\w\.]+)$',
        views.index,
        name='domain_index'
    ),
    url(
        r'^recently-collected$',
        views.recently_collected_domains,
        name='recently_collected_domains'
    ),
    url(
        r'^(?P<domain>[\w\.]+)/data$',
        views.collected_pages,
        name='collected_pages'
    ),
    url(
        r'^(?P<domain>[\w\.]+)/(?P<id>\d+)/thumbnail.png$',
        views.page_thumbnail,
        name='page_thumbnail'
    ),

    url(
        r'^(?P<domain>[\w\.]+)/(?P<id>\d+)/screenshot.png$',
        views.page_thumbnail,
        name='page_screenshot'
    ),
    # url(
    #     r'^(?P<domain>[\w\.]+)$',
    #     views.collected_domain,
    #     name='collected_domain'
    # ),
)
