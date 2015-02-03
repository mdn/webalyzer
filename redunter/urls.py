from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = patterns('',
    url(
        r'collector/',
        include('redunter.collector.urls', namespace='collector')
    ),
    url(
        r'analyzer/',
        include('redunter.analyzer.urls', namespace='analyzer')
    ),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
