from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import discussion.views as views

urlpatterns = [
    # url(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    # url(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),

]

