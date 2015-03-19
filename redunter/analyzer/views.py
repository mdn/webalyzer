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

from django import http
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Sum, Max
from django.db import transaction
from django.core.cache import cache
from django.utils.encoding import smart_unicode

from redunter.collector.models import Page
from redunter.analyzer.models import Result, Suspect
# from redunter.base.helpers import diff_table

gator = Gator(settings.ALLIGATOR_CONN)


def diff_table(before, after):
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        lineterm='',
        fromfile='original', tofile='optimized'
    )
    return '\n'.join(diff)


@contextmanager
def tmpfilename(content, extension=''):
    filename = hashlib.md5(content.encode('utf-8')).hexdigest()
    if extension:
        filename += '.%s' % (extension,)
    dir_ = tempfile.mkdtemp()
    filepath = os.path.join(dir_, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    try:
        yield filepath
    finally:
        shutil.rmtree(dir_)


def prettify_css(css):
    with tmpfilename(css, 'css') as filename:
        process= subprocess.Popen(
            ['crass', filename, '--pretty'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
        if not stdout and stderr:
            raise Exception(stderr)  # ???
        return stdout


class ExtendedProcessor(Processor):

    download_cache = {}
    root = os.path.join(tempfile.gettempdir(), 'mincss_download')

    def download(self, url):
        cached = self.download_cache.get(url)
        if cached:
            ts, content = cached
            age = time.time() - ts
            # this caching stuff is pointless unless the caching it
            # written to disk or something
            if age < 3600:
                print "CACHE HIT", url
                return content
        filepath = self._get_filepath(url)
        if os.path.isfile(filepath):
            age = time.time() - os.stat(filepath)[stat.ST_MTIME]
            if age > 3600:
                print "FILECACHE MISS", url
                os.remove(filepath)
            else:
                print "FILECACHE HIT", url
                with codecs.open(filepath, 'r', 'utf-8') as f:
                    return f.read()

        r = requests.get(url, verify=not settings.DEBUG)
        content = r.content
        if isinstance(content, str):
            content = smart_unicode(content, r.encoding)

        if r.status_code < 400:
            self.download_cache[url] = (time.time(), content)
            print "CACHE MISS", url
            with codecs.open(filepath, 'w', 'utf-8') as f:
                f.write(content)
            return content
        else:
            raise DownloadError("%s - %s" % (r.status_code, url))

    def _get_filepath(self, url):
        hashed = hashlib.md5(url).hexdigest()
        dir_ = os.path.join(self.root, hashed[0])
        if not os.path.isdir(dir_):
            os.makedirs(dir_)
        return os.path.join(dir_, hashed[1:] + '.css')


def index(request, *args, **kwargs):
    # the *args, **kwargs is because this view is used in urls.py
    # as a catch-all for the sake of pushstate
    context = {}
    html_formatter = HtmlFormatter(linenos=True)
    context['pygments_css'] = html_formatter.get_style_defs('.highlight')
    return render(request, 'analyzer/index.html', context)


@json_view
def recent_submissions(request):
    context = {}
    results = (
        Result.objects.values('domain')
        .annotate(m=Max('modified'))
        .order_by('-m')
    )
    context['domains'] = [x['domain'] for x in results]
    return context


@json_view
@transaction.atomic
def submit(request):
    context = {}
    if request.method != 'POST':  # required_P
        return redirect(reverse('analyzer:start'))

    POST = json.loads(request.body)
    # print request.POST.items()
    domain = POST['domain']
    gator.task(
        start_analysis,
        domain,
    )
    jobs_ahead = cache.get('jobs_ahead', 0)
    return {
        'jobs_ahead': jobs_ahead,
    }


def start_analysis(domain):
    pages = Page.objects.filter(domain=domain)
    processor = ExtendedProcessor()
    t0 = time.time()
    for page in pages:
        try:
            processor.process_html(page.html, page.url)
        except DownloadError as err:
            print "Failed to downlod on", page.url
            print err
            raise
    t1 = time.time()
    processor.process()
    t2 = time.time()
    print t2-t1
    print t1-t0
    print
    # delete all old analysises
    Result.objects.filter(domain=domain).delete()

    for inline in processor.inlines:
        result = Result.objects.create(
            domain=domain,
            url=inline.url,
            line=inline.line,
            before=smart_unicode(inline.before),
            after=smart_unicode(inline.after),
        )
        selectors = OrderedDict(get_selectors(result.before))
        after = set(
            x[0] for x in get_selectors(
                result.after
            )
        )
        removed_keys = set(selectors.keys()) - after
        lines = result.before.splitlines()

        for key in removed_keys:
            selector, style = selectors[key]
            line = None
            for i, line_ in enumerate(lines):
                if line_.startswith(selector):
                    line = i + 1
                    break

            Suspect.objects.create(
                result=result,
                selector=key,
                selector_full=selector,
                style=style,
                line=line
            )

    for link in processor.links:
        result = Result.objects.create(
            domain=domain,
            url=link.href,
            before=smart_unicode(link.before),
            after=smart_unicode(link.after),
        )
        selectors = OrderedDict(get_selectors(
            result.before, result.url
        ))
        after = set(
            x[0] for x in get_selectors(
                result.after, result.url
            )
        )
        removed_keys = set(selectors.keys()) - after
        lines = result.before.splitlines()

        for key in removed_keys:
            selector, style = selectors[key]
            line = None
            for i, line_ in enumerate(lines):
                if line_.startswith(selector):
                    line = i + 1
                    break

            Suspect.objects.create(
                result=result,
                selector=key,
                selector_full=selector,
                style=style,
                line=line
            )

        # return redirect('analyzer:analyzed', domain)


def get_selectors(csstext, href=None):
    sheet = cssutils.parseString(
        csstext,
        href=href
    )
    for rule in sheet.cssRules:
        if rule.type != rule.STYLE_RULE:
            continue
        style = rule.style.cssText
        for selector in rule.selectorList:
            yield (selector.selectorText, (rule.selectorText, style))


@json_view
def analyzed(request, domain):
    results = Result.objects.filter(domain=domain)
    if not results.count():
        return {'count': 0}

    pages = Page.objects.filter(domain=domain)
    context = {}
    summed_results = results.extra(
        select={
            'sum_before': 'sum(LENGTH(before))',
            'sum_after': 'SUM(LENGTH(after))',
        }
    )
    # summed_results = summed_results.order_by(False)
    summed = summed_results.values('sum_before', 'sum_after')[0]
    context['total_before'] = summed['sum_before']
    context['total_after'] = summed['sum_after']
    # context['total_potential_saving'] = (context['total_before'] -
    # context['total_potential_saving'] = (
    #     results.aggregate(
    #         Sum('potential_saving')
    #     )['potential_saving__sum']
    # )
    all_results = []
    for result in results.order_by('modified'):
        suspects = []
        for suspect in result.suspects:
            suspects.append({
                'selector': suspect.selector,
                'selector_full': suspect.selector_full,
                'style': suspect.style,
                'line': suspect.line,
                'size': suspect.size,
            })
        if result.url.endswith('min.css'):
            prettified = True
            diff = diff_table(
                prettify_css(result.before),
                prettify_css(result.after)
            )
        else:
            prettified = False
            diff = diff_table(result.before, result.after)
        filename = None
        if not result.line:
            filename = os.path.basename(result.url)
        all_results.append({
            'id': result.id,
            'url': result.url,
            'line': result.line,
            'size_before': len(result.before),
            'size_after': len(result.after),
            # 'before': result.before,
            # 'after': result.after,
            # 'diff': result.unified_diff,
            'unified_diff': diff,
            'ignored': result.ignored,
            'modified': result.modified,
            'suspects': suspects,
            'prettified': prettified,
            'filename': filename,
        })

    # all_pages = []
    # for page in pages:
    #     all_pages.append({
    #         'domain': page.domain,
    #         'url': page.url,
    #         'html':
    #     })

    context['domain'] = domain
    context['results'] = all_results
    context['pages_count'] = pages.count()
    # print context
    return context
    # return render(request, 'analyzer/analyzed.html', context)

@json_view
def source_view(request, domain, id):
    result = get_object_or_404(Result, id=id)
    assert result.domain == domain, result.domain
    context = {}

    html_formatter = HtmlFormatter(
        linenos=True,
        lineanchors='L',
        linespans='L',
        anchorlinenos=True
    )
    context['code'] = highlight(
        result.before,
        CssLexer(),
        html_formatter
    )
    context['domain'] = domain
    context['result'] = {
        'id': result.id,
        'url': result.url,
    }
    return context


def diff_view(request, domain, id):
    result = get_object_or_404(Result, id=id, domain=domain)
    context = {}

    html_formatter = HtmlFormatter(
        linenos=True,
        lineanchors='L',
        linespans='L',
        anchorlinenos=True
    )
    context['code'] = highlight(
        diff_table(result.before, result.after),
        DiffLexer(),
        html_formatter
    )
    context['domain'] = domain
    context['result'] = result
    context['pygments_css'] = html_formatter.get_style_defs('.highlight')
    return render(request, 'analyzer/diff_view.html', context)


def download(request, domain, id, which, filename):
    result = get_object_or_404(Result, id=id, domain=domain)
    assert filename.lower().endswith('.css'), filename

    if which == 'before':
        content = result.before
    elif which == 'after':
        content = result.after
    else:
        raise NotImplementedError(which)

    if 'pretty' in request.GET:
        content = prettify_css(content)
    
    response = http.HttpResponse(
        content,
        content_type='text/css; charset=utf-8'
    )
    response['Content-Disposition'] = 'inline; filename=%s' % (filename,)
    return response
