import os
import json
import difflib
import hashlib
import tempfile
import subprocess
import shutil
from contextlib import contextmanager

from pygments import highlight
from pygments.lexers import CssLexer, DiffLexer
from pygments.formatters import HtmlFormatter
from jsonview.decorators import json_view

from django import http
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.db import transaction
from django.core.cache import cache

from webalyzer.collector.models import Page
from webalyzer.analyzer.models import Result
from .tasks import start_analysis
# from webalyzer.base.helpers import diff_table


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
        process = subprocess.Popen(
            ['crass', filename, '--pretty'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
        if not stdout and stderr:
            raise Exception(stderr)  # ???
        return stdout


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
    if request.method != 'POST':  # required_P
        return redirect(reverse('analyzer:start'))

    POST = json.loads(request.body)
    domain = POST['domain']
    start_analysis.delay(domain)
    jobs_ahead = cache.get('jobs_ahead', 0)
    return {
        'jobs_ahead': jobs_ahead,
    }


@json_view
def analyzed(request, domain):
    # from time import sleep
    # sleep(3)
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

    context['domain'] = domain
    context['results'] = all_results
    context['pages_count'] = pages.count()
    return context


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
