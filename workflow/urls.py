from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import workflow.views as views

urlpatterns = [
    # url(r'^_discussion_comment_draft', views.update_discussion_comment_draft, name="discussion-comment-draft"),
    # url(r'^_discussion_comment_submit', views.submit_discussion_comment, name="discussion-comment-submit"),
    url(r'^(?P<workflowinstance_id>.*)/set_workflowinstance_feature_completed', views.set_workflowinstance_feature_completed, name="set_workflowinstance_feature_completed"),

    url(r'^recipes/all$', views.workflowrecipes_all, name="workflowrecipes_all"),
    url(r'^recipes/manage$', views.manage_recipe, name='manage_recipe'),
    url(r'^recipes/(?P<pk>.*)/edit$', views.edit_recipe, name="edit_recipe"),
    url(r'^recipes/(?P<pk>.*)/delete$', views.delete_recipe, name="delete_recipe"),
    url(r'^recipes/(?P<pk>.*)/duplicate$', views.duplicate_recipe, name="duplicate_recipe"),
    url(r'^recipes/(?P<pk>.*)/create_workflowimage$', views.create_workflowimage, name="create_workflowimage"),
    url(r'^recipes/(?P<pk>.*)/create_workflowinstance_from_recipe$', views.create_workflowinstance_from_recipe, name="create_workflowinstance_from_recipe"), 
    url(r'^recipes/(?P<pk>.*)/create_system_worflowinstances_from_recipe$', views.create_system_worflowinstances_from_recipe, name="create_system_worflowinstances_from_recipe"),

    url(r'^images/all$', views.workflowimages_all, name="workflowimages_all"),
    url(r'^images/(?P<pk>.*)/create_workflowinstance$', views.create_workflowinstance, name="create_workflowinstance"),
    url(r'^images/(?P<pk>.*)/delete$', views.delete_workflowimage, name="delete_workflowimage"),
    url(r'^images/(?P<pk>.*)/create_workflowrecipe$', views.create_workflowrecipe_from_image, name="create_workflowrecipe_from_image"),
    url(r'^images/(?P<pk>.*)/create_system_worflowinstances$', views.create_system_worflowinstances, name="create_system_worflowinstances"),

    url(r'^instances/all$', views.workflowinstances_all, name="workflowinstances_all"),

    # url(r'^store/(?P<source_slug>.*)/(?P<app_name>.*)$', views.apps_catalog_item),

]

