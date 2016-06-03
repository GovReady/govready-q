from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'(\d+)/([\w_-]+)(/start)?$', guidedmodules.views.next_question),
    url(r'start$', guidedmodules.views.new_task),
    url(r'_change_state$', guidedmodules.views.change_task_state, name="task_change_state"),
]

