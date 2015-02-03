import difflib

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe
from django.template.defaultfilters import filesizeformat
from jingo import register

static = register.function(static)
filesizeformat = register.function(filesizeformat)


@register.function
def diff_table(before, after):
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        lineterm=''
    )
    s = '\n'.join(diff)
    return s
