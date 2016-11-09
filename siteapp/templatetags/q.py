from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    import CommonMark
    return mark_safe(CommonMark.commonmark(str(value), safe_mode=True))

@register.filter(is_safe=True)
def json(value):
    import json
    return mark_safe(json.dumps(value))

