import time

from jsonview.decorators import json_view
from sorl.thumbnail import get_thumbnail

from django import http
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Max
from django.core.cache import cache
from django.core.paginator import Paginator

from webalyzer.collector.models import Page
from webalyzer.collected.models import Screenshot

from .tasks import find_page_title, generate_screenshot


def index(request, *args, **kwargs):
    # the *args, **kwargs is because this view is used in urls.py
    # as a catch-all for the sake of pushstate
    context = {}
    # html_formatter = HtmlFormatter(linenos=True)
    # context['pygments_css'] = html_formatter.get_style_defs('.highlight')
    return render(request, 'collected/index.html', context)


@json_view
def recently_collected_domains(request):
    # TODO this'll be based on auth or something instead
    context = {}
    results = (
        Page.objects.values('domain')
        .annotate(m=Max('modified'))
        .order_by('-m')
    )
    context['domains'] = [x['domain'] for x in results]
    return context


@json_view
def collected_pages(request, domain):
    pages = Page.objects.filter(domain=domain)
    context = {}
    context['total_html_size'] = pages.aggregate(Sum('size'))['size__sum']

    context['domain'] = domain
    # context['results'] = all_results
    context['pages_count'] = pages.count()
    p = Paginator(pages.order_by('-modified'), 10)
    page = int(request.GET.get('page', 1))
    some_pages = []
    missing_titles = []
    for page in p.page(page).object_list:
        some_pages.append({
            'id': page.id,
            'url': page.url,
            'title': page.title,
            'size': page.size,
            'added': page.added.isoformat(),
            'modified': page.modified.isoformat(),
        })
        if page.title is None:
            missing_titles.append(page.id)
            find_page_title.delay(page.id)
            # find_page_title(page.id)

    context['pages'] = some_pages
    context['missing_title'] = missing_titles

    return context


def page_thumbnail(request, domain, id):
    dimensions = request.GET.get('dimensions')
    page = get_object_or_404(Page, domain=domain, id=id)

    screenshot = Screenshot.get(page)
    if screenshot:
        if dimensions:
            thumb = get_thumbnail(
                screenshot.file,
                dimensions,
                # crop='center',
                crop='top',
                quality=80,
            )
            r = http.HttpResponse(content_type='image/png')
            r.write(thumb.read())
            return r
        else:
            return http.FileResponse(screenshot.file, content_type='image/png')

    else:
        cache_key = 'generating_screenshot_{}'.format(page.id)
        if not cache.get(cache_key):
            cache.set(cache_key, str(time.time()), 60)
            generate_screenshot.delay(page.id)
        return http.FileResponse(
            open('static/collected/images/image.png', 'rb'),
            content_type='image/png'
        )


# @json_view
# def source_view(request, domain, id):
#     result = get_object_or_404(Result, id=id)
#     assert result.domain == domain, result.domain
#     context = {}
#
#     html_formatter = HtmlFormatter(
#         linenos=True,
#         lineanchors='L',
#         linespans='L',
#         anchorlinenos=True
#     )
#     context['code'] = highlight(
#         result.before,
#         CssLexer(),
#         html_formatter
#     )
#     context['domain'] = domain
#     context['result'] = {
#         'id': result.id,
#         'url': result.url,
#     }
#     return context
