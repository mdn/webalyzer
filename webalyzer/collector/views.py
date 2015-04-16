import json
from urlparse import urlparse

from django.shortcuts import render
from django import http
from django.views.decorators.csrf import csrf_exempt

from webalyzer.collector.models import Page, Stylesheet

@csrf_exempt
def collect(request):
    if request.method in ('GET', 'HEAD'):
        response = http.HttpResponse('Works')
        response['Access-Control-Allow-Origin'] = '*'
        return response

    url = request.POST['url']
    domain = request.POST.get('domain', urlparse(url).netloc)
    # print (url, domain)

    if request.POST.get('css'):
        # it's a stylesheet!
        css = request.POST['css']
        for page in Stylesheet.objects.filter(url=url, domain=domain):
            if page.css == css:
                created = False
                break
        else:
            page = Stylesheet.objects.create(
                url=url,
                domain=domain,
                css=css,
            )
            created = True

        if created:
            print "New CSS", domain, url
            print len(page), "bytes"
        else:
            print "Not new CSS", domain, url

    else:
        html = request.POST['html']
        for page in Page.objects.filter(url=url, domain=domain):
            if page.html == html:
                created = False
                break
        else:
            page = Page.objects.create(
                url=url,
                domain=domain,
                html=html,
            )
            created = True

        if created:
            print "New HTML", domain, url
            print len(page), "bytes"
        else:
            print "Not new HTML", domain, url

    response = http.HttpResponse(
        'OK', status=created and 201 or 200)
    response['Access-Control-Allow-Origin'] = '*'
    return response
