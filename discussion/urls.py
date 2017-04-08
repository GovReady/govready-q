from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import discussion.views as views

urlpatterns = [
    url(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    url(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    url(r'^_discussion_comment_edit', views.edit_discussion_comment, name="discussion-comment-edit"),
    url(r'^_discussion_comment_delete', views.delete_discussion_comment, name="discussion-comment-delete"),
    url(r'^_discussion_comment_react', views.save_reaction, name="discussion-comment-react"),
    url(r'^_discussion_comment_attachments', views.create_attachments, name="discussion-comment-create-attachments"),
    url(r'^_discussion_poll', views.poll_for_events, name="discussion_poll_for_events"),
    url(r'^attachment/(\d+)', views.download_attachment, name="discussion-attachment"),
]

