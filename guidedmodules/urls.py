from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'(\d+)/([\w_-]+)$', guidedmodules.views.next_question),
    url(r'start$', guidedmodules.views.new_task),
    url(r'new-project$', guidedmodules.views.new_project),
    url(r'_send_invitation$', guidedmodules.views.send_invitation, name="send_invitation"),
    url(r'_cancel_invitation$', guidedmodules.views.cancel_invitation, name="cancel_invitation"),
    url(r'accept-invitation/(?P<code>.*)$', guidedmodules.views.accept_invitation, name="accept_invitation"),
    url(r'start-discussion', guidedmodules.views.start_a_discussion, name="start_a_discussion"),
    url(r'submit-comment', guidedmodules.views.submit_discussion_comment, name="submit-comment"),
]

