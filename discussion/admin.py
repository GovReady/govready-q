from django.contrib import admin

from .models import Discussion, Comment, Attachment

class DiscussionAdmin(admin.ModelAdmin):
	list_display = ('attached_to', 'created')
	readonly_fields = ('attached_to_content_type', 'attached_to_object_id', 'guests', 'extra')

class CommentAdmin(admin.ModelAdmin):
	list_display = ('discussion', 'user', 'text')
	readonly_fields = ('discussion', 'user', 'replies_to')
	fieldsets = [
		(None, { "fields": ('discussion', 'user', 'replies_to',)}),
		(None, { "fields": ('text', 'emojis', 'proposed_answer')}),
		(None, { "fields": ('deleted', 'extra')}),
	]

class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'discussion', 'comment', 'user', 'file')
	readonly_fields = ('id', 'discussion', 'comment', 'user', 'file')

admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Attachment, AttachmentAdmin)
