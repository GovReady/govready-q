from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_notification_link(obj, notification):
	# If the target says that it cannot generate a link,
	# then return None.
	if hasattr(obj, 'supress_link_from_notifications'):
		if obj.supress_link_from_notifications:
			return None

	# If the target has a function specifically for making
	# links for notifications, use that. It can return None
	# to indicate that we should fall back to get_absolute_url.
	if hasattr(obj, 'get_notification_link'):
		ret = obj.get_notification_link(notification)
		if ret:
			return ret

	# Use get_absolute_url.
	return obj.get_absolute_url()
