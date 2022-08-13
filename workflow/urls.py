from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import workflow.views as views

urlpatterns = [
    # url(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    # url(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    url(r'^(?P<workflowinstance_id>.*)/set_workflowinstance_feature_completed', views.set_workflowinstance_feature_completed, name="set_workflowinstance_feature_completed")

    # url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

]

