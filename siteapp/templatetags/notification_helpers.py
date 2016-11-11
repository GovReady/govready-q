from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_notification_link(obj, notification):
	if hasattr(obj, 'get_notification_link'):
		ret = obj.get_notification_link(notification)
		if ret:
			return ret
	return obj.get_absolute_url()
