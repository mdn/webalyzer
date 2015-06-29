from urlparse import urlparse

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
    source_hash = request.POST['source_hash']
    # print (url, domain)

    if request.POST.get('css'):
        # it's a stylesheet!
        css = request.POST['css']
        for page in Stylesheet.objects.filter(
                url=url,
                domain=domain,
                source_hash=source_hash):
            if page.css == css:
                created = False
                break
        else:
            page = Stylesheet.objects.create(
                url=url,
                domain=domain,
                source_hash=source_hash,
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
        for page in Page.objects.filter(
                url=url,
                domain=domain,
                source_hash=source_hash):
            if page.html == html:
                created = False
                break
        else:
            page = Page.objects.create(
                url=url,
                domain=domain,
                source_hash=source_hash,
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


def collect_check(request, source_hash, source_type, domain):
    source_hash = int(source_hash)
    matches = 0

    # do we have a counter to increment?
    # do we want to update the date?

    if source_type == 'css':
        matches = Stylesheet.objects.filter(source_hash=source_hash,
                                            domain=domain)
    elif source_type == 'html':
        matches = Page.objects.filter(source_hash=source_hash, domain=domain)

    if matches.exists():
        response = http.HttpResponse('OK', status=200)
    else:
        response = http.HttpResponse('Not Found', status=404)

    response['Access-Control-Allow-Origin'] = '*'

    return response
