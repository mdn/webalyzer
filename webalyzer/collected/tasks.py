import os
import subprocess
import urlparse
import shutil
import tempfile
from contextlib import contextmanager

from lxml import etree
from lxml.cssselect import CSSSelector
from celery import shared_task

# from django.conf import settings
from django.core.files import File

from webalyzer.collected.models import Screenshot
from webalyzer.collector.models import Page


@contextmanager
def tmpdir(*args, **kwargs):
    dir_ = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield dir_
    finally:
        # print "DELETE", dir_
        shutil.rmtree(dir_)


@shared_task
def find_page_title(page_id):
    page = Page.objects.get(id=page_id)
    parser = etree.HTMLParser()
    html = page.html.strip()
    tree = etree.fromstring(html, parser).getroottree()
    dom = tree.getroot()

    for element in CSSSelector('title')(dom):
        page.title = element.text.strip()
        page.save()
        return


@shared_task
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
            Screenshot.objects.create(
                page=page,
                file=File(f),
                width=width,
                height=height,
                engine='phantomjs'
            )
