from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def first_line_only(value):
    # Return text up to first carriage return
    split_prompt = value.split('\n')
    if len(split_prompt) == 1:
        return split_prompt[0]
    else:
        return split_prompt[0]+"..."
