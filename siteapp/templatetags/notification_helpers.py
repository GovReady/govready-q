from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from siteapp.models import ProjectMembership

register = template.Library()

@register.filter
def has_membership(project, user):
    return True if ProjectMembership.objects.filter(project=project, user=user) else False

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

def render_markdown_instead_of_escaping(parser, token):
	class Node(template.Node):
		def __init__(self, variable_name):
			self.variable = template.Variable(variable_name)
		def render(self, context):
			md = self.variable.resolve(context)
			if not context.autoescape:
				# Auto-escaping is off, so we're in the text portion
				# of a notification email. Return the raw markdown.
				return md
			else:
				# Auto-escaping is on, so we're in the HTML portion
				# of a notification email. Rather than returning the
				# raw Markdown, which will look funny because e.g.
				# line breaks will be ignored when it is placed within
				# HTML, render the Markdown to HTML. Turn on safe mode
				# since the content can't be trusted.
				import commonmark
				return commonmark.HtmlRenderer({ "safe": True })\
					.render(commonmark.Parser().parse(md))
	try:
		tag_name, variable_name = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError(
			"%r tag requires a single argument naming a variable" % token.contents.split()[0]
		)
	return Node(variable_name)
register.tag('render_markdown_instead_of_escaping', render_markdown_instead_of_escaping)
