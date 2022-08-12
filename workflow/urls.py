from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import workflow.views as views

urlpatterns = [
    # url(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    # url(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    url(r'^(?P<workflowinstance_id>.*)/advance', views.workflowinstance_advance, name="workflowinstance_advance")

    # url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

]

