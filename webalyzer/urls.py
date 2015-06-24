from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = patterns(
    '',
    url(
        r'collector/',
        include('webalyzer.collector.urls', namespace='collector')
    ),
    url(
        r'collected/',
        include('webalyzer.collected.urls', namespace='collected')
    ),
    url(
        r'analyzer/',
        include('webalyzer.analyzer.urls', namespace='analyzer')
    ),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


import djcelery
djcelery.setup_loader()
