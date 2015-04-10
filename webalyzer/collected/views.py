import os
import json
import time
import difflib
import codecs
import hashlib
import stat
import tempfile
import subprocess
import shutil
import urlparse
from collections import OrderedDict
from contextlib import contextmanager

import requests
from mincss.processor import Processor, DownloadError
import cssutils
from pygments import highlight
from pygments.lexers import CssLexer, DiffLexer
from pygments.formatters import HtmlFormatter
from alligator import Gator
from jsonview.decorators import json_view
from lxml import etree
from lxml.cssselect import CSSSelector
from sorl.thumbnail import get_thumbnail

from django import http
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Sum, Max
from django.db import transaction
from django.core.cache import cache
from django.utils.encoding import smart_unicode
from django.core.paginator import Paginator
from django.core.files import File

from webalyzer.collector.models import Page
from webalyzer.collected.models import Screenshot
from webalyzer.analyzer.models import Result, Suspect


gator = Gator(settings.ALLIGATOR_CONN)


@contextmanager
def tmpdir(*args, **kwargs):
    dir_ = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield dir_
    finally:
        # print "DELETE", dir_
        shutil.rmtree(dir_)


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
            gator.task(
                find_page_title,
                page.id
            )
            # find_page_title(page.id)

    context['pages'] = some_pages
    context['missing_title'] = missing_titles

    return context


def find_page_title(page_id):
    page = Page.objects.get(id=page_id)
    parser = etree.HTMLParser()
    html = page.html.strip()
    tree = etree.fromstring(html, parser).getroottree()
    dom = tree.getroot()
    # lxml inserts a doctype if none exists, so only include it in
    # the root if it was in the original html.
    root = tree if html.startswith(tree.docinfo.doctype) else dom

    for element in CSSSelector('title')(dom):
        page.title = element.text.strip()
        page.save()
        return


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
            gator.task(
                generate_screenshot,
                page.id
            )
        return http.FileResponse(
            open('static/collected/images/image.png', 'rb'),
            content_type='image/png'
        )


def generate_screenshot(page_id):
    print "Generating screenshot for", page_id
    page = Page.objects.get(id=page_id)
    parser = etree.HTMLParser()
    html = page.html.strip()
    if not html.lower().startswith('<!doctype'):
        html = '<!doctype html>\n' + html
    tree = etree.fromstring(html, parser).getroottree()
    dom = tree.getroot()
    # lxml inserts a doctype if none exists, so only include it in
    # the root if it was in the original html.
    root = tree if html.startswith(tree.docinfo.doctype) else dom

    # remove all scripts
    for script in CSSSelector('script')(dom):
        script.getparent().remove(script)
    for element in CSSSelector('img[src]')(dom):
        element.attrib['src'] = urlparse.urljoin(
            page.url,
            element.attrib['src']
        )
    for element in CSSSelector('link[href]')(dom):
        if not element.attrib.get('rel') == 'stylesheet':
            continue
        element.attrib['href'] = urlparse.urljoin(
            page.url,
            element.attrib['href']
        )

    with tmpdir(str(page.id)) as dir_:
        html_file = os.path.join(
            dir_,
            'page-{}.html'.format(page.id)
        )
        png_file = os.path.join(
            dir_,
            'screenshot-{}.png'.format(page.id)
        )
        with open(html_file, 'w') as f:
            f.write('<!doctype html>\n')
            f.write(etree.tostring(
                root,
                pretty_print=False,
                method='html',
                encoding='utf-8',
            ))

        # that 'screenshot.js' file is in the same directory as this file
        _here = os.path.dirname(__file__)
        width, height = 1400, 900
        cmd = [
            'phantomjs',
            '--ignore-ssl-errors=yes',
            os.path.join(_here, 'screenshot.js'),
            html_file,
            png_file,
            str(width),
            str(height)
        ]
        # print cmd
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        # print (stdout, stderr)
        if not os.path.isfile(png_file):
            raise Exception("No PNG file created")

        with open(png_file, 'rb') as f:
            screenshot = Screenshot.objects.create(
                page=page,
                file=File(f),
                width=width,
                height=height,
                engine='phantomjs'
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
