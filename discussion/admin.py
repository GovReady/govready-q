from django.contrib import admin

from .models import Discussion, Comment, Attachment
from django_json_widget.widgets import JSONEditorWidget
from jsonfield import JSONField

class DiscussionAdmin(admin.ModelAdmin):
	list_display = ('attached_to', 'created')
	readonly_fields = ('attached_to_content_type', 'attached_to_object_id', 'guests', 'extra')
	formfield_overrides = {
		JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 20em; width: 650px; margin-left: 160px;'})},
	}


class CommentAdmin(admin.ModelAdmin):
	list_display = ('discussion', 'user', 'created', 'draft', 'deleted')
	readonly_fields = ('discussion', 'user', 'replies_to')
	fieldsets = [
		(None, { "fields": ('discussion', 'user', 'replies_to',)}),
		(None, { "fields": ('text', 'emojis', 'proposed_answer')}),
		(None, { "fields": ('deleted', 'extra')}),
	]
	formfield_overrides = {
		JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 20em; width: 650px; margin-left: 160px;'})},
	}


class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'comment', 'user')
	fieldsets = [ # hide the file field because we can't render it
		(None, { "fields": ('id', 'comment', 'user') })
	]
	readonly_fields = ('id', 'comment', 'user')
	formfield_overrides = {
		JSONField: {'widget': JSONEditorWidget(attrs={'style': 'height: 20em; width: 650px; margin-left: 160px;'})},
	}


admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attachment, AttachmentAdmin)
