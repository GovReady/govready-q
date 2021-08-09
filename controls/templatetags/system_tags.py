from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def json(value):
    # Encode value as JSON for inclusion within a <script></script> tag.
    # Since we are not using |escapejs (which would only be valid within
    # strings), we must instead ensure that the literal "</script>" doesn't
    # occur within the JSON content since that would break out of the script
    # tag. This could occur both in string values and in the keys of objects.
    # Since < and > can only occur within strings (i.e. they're not valid
    # characters otherwise), we can JSON-escape them after serialization.
    import json
    value = json.dumps(value, sort_keys=True)
    value = value.replace("<", r'\u003c')
    value = value.replace(">", r'\u003e') # not necessary but for good measure
    value = value.replace("&", r'\u0026') # not necessary but for good measure
    return mark_safe(value) # nosec

@register.filter(is_safe=True)
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def divide(value, arg):
    if value is None:
        value = 0
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)