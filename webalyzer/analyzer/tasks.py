import os
import stat
import codecs
import hashlib
import tempfile
import time
from collections import OrderedDict

from django.utils.encoding import smart_unicode
from django.conf import settings

import requests
import cssutils
from celery import shared_task
from mincss.processor import Processor, DownloadError

from webalyzer.collector.models import Page
from webalyzer.analyzer.models import Result, Suspect


@shared_task
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
