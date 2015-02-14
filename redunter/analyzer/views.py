import time
from collections import OrderedDict

import requests
from mincss.processor import Processor, DownloadError
import cssutils

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Sum, Max
from django.db import transaction

from redunter.collector.models import Page
from redunter.analyzer.models import Result, Suspect


class ExtendedProcessor(Processor):

    download_cache = {}

    def download(self, url):
        cached = self.download_cache.get(url)
        if cached:
            ts, content = cached
            age = time.time() - ts
            if age < 3600:
                return content

        r = requests.get(url, verify=not settings.DEBUG)
        if r.status_code < 400:
            self.download_cache[url] = (time.time(), r.content)
            return r.content
        else:
            raise DownloadError("%s - %s" % (r.status_code, url))


def start(request):
    if request.method == 'POST':
        # Ideally here we'd start a message queue process
        pass
    context = {}
    recent_domains = (
        Result.objects.values('domain')
        .annotate(m=Max('modified'))
        .order_by('-m')
    )

    context['recent_domains'] = [x['domain'] for x in recent_domains]
    return render(request, 'analyzer/start.html', context)


@transaction.atomic
def analyze(request):
    context = {}
    if request.method != 'POST':
        return redirect(reverse('analyzer:start'))

    domain = request.POST['domain']
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
            before=inline.before,
            after=inline.after,
        )
        selectors = OrderedDict(get_selectors(inline.before))
        after = set(
            x[0] for x in get_selectors(
                inline.after
            )
        )
        removed_keys = set(selectors.keys()) - after
        lines = inline.before.splitlines()

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
            before=link.before,
            after=link.after,
        )
        selectors = OrderedDict(get_selectors(
            link.before, link.href
        ))
        after = set(
            x[0] for x in get_selectors(
                link.after, link.href
            )
        )
        removed_keys = set(selectors.keys()) - after
        lines = link.before.splitlines()

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

        return redirect('analyzer:analyzed', domain)


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


def analyzed(request, domain):
    results = Result.objects.filter(domain=domain)
    if not results.count():
        return redirect('analyzer:start')
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
    context['domain'] = domain
    context['results'] = results.order_by('modified')
    context['pages'] = pages
    return render(request, 'analyzer/analyzed.html', context)


def source_view(request, domain, id):
    result = get_object_or_404(Result, id=id)
    assert result.domain == domain, result.domain
    context = {}
    from pygments import highlight
    from pygments.lexers import CssLexer
    from pygments.formatters import HtmlFormatter

    html_formatter = HtmlFormatter(linenos=True)
    context['code'] = highlight(
        result.before,
        CssLexer(),
        html_formatter
    )
    context['domain'] = domain
    context['result'] = result
    context['pygments_css'] = html_formatter.get_style_defs('.highlight')
    return render(request, 'analyzer/source_view.html', context)
