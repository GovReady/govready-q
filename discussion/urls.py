from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import discussion.views as views

urlpatterns = [
    url(r'start-discussion', views.start_a_discussion, name="start_a_discussion"),
    url(r'_discussion_comment_create', views.submit_discussion_comment, name="discussion-comment-create"),
    url(r'_discussion_comment_edit', views.edit_discussion_comment, name="discussion-comment-edit"),
    url(r'_discussion_comment_delete', views.delete_discussion_comment, name="discussion-comment-delete"),
]

