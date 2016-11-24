from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'^(\d+)/([\w_-]+)$', guidedmodules.views.next_question),
    url(r'^start$', guidedmodules.views.new_task),
    url(r'^_change_state$', guidedmodules.views.change_task_state, name="task_change_state"),
    url(r'^_instrumentation_record_interaction$', guidedmodules.views.instrumentation_record_interaction, name="task_instrumentation_record_interaction"),
    url(r'^_start_discussion', guidedmodules.views.start_a_discussion, name="start_a_discussion"),
    url(r'^analytics$', guidedmodules.views.analytics, name="guidedmodules_analytics"),
]

