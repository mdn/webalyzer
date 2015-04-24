import difflib

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.defaultfilters import filesizeformat
from jingo import register

static = register.function(static)
filesizeformat = register.function(filesizeformat)


@register.function
def count_diff_lines(before, after):
    ndiff = difflib.ndiff(before.splitlines(), after.splitlines())
    return len(list(ndiff))


@register.function
def diff_table(before, after):
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        lineterm='',
        fromfile='original', tofile='optimized'
    )
    return '\n'.join(diff)
