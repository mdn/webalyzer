import json
from urlparse import urlparse

from django.shortcuts import render
from django import http
from django.views.decorators.csrf import csrf_exempt

from webalyzer.collector.models import Page

@csrf_exempt
def collect(request):
    if request.method in ('GET', 'HEAD'):
        response = http.HttpResponse('Works')
        response['Access-Control-Allow-Origin'] = '*'
        return response

    url = request.POST['url']
    html = request.POST['html']
    domain = urlparse(url).netloc
    print (url, domain)

    for page in Page.objects.filter(url=url, domain=domain):
        if page.html == html:
            created = False
            break
    else:
        page = Page.objects.create(
            url=url,
            domain=domain,
            html=html,
            size=len(html),
        )
        created = True

    print "Created?", created
    print len(page.html), "bytes of HTML"
    response = http.HttpResponse(
        'OK', status=created and 201 or 200)
    response['Access-Control-Allow-Origin'] = '*'
    return response
