from django.contrib import admin

from .models import Discussion, Comment, Attachment

class DiscussionAdmin(admin.ModelAdmin):
	list_display = ('attached_to', 'created')
	readonly_fields = ('attached_to_content_type', 'attached_to_object_id', 'guests', 'extra')

class CommentAdmin(admin.ModelAdmin):
	list_display = ('discussion', 'user', 'created', 'draft', 'deleted')
	readonly_fields = ('discussion', 'user', 'replies_to')
	fieldsets = [
		(None, { "fields": ('discussion', 'user', 'replies_to',)}),
		(None, { "fields": ('text', 'emojis', 'proposed_answer')}),
		(None, { "fields": ('deleted', 'extra')}),
	]

class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'comment', 'user')
	fieldsets = [ # hide the file field because we can't render it
		(None, { "fields": ('id', 'comment', 'user') })
	]
	readonly_fields = ('id', 'comment', 'user')

admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attachment, AttachmentAdmin)
