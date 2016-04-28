from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'(\d+)/([\w_-]+)$', guidedmodules.views.next_question),
    url(r'start$', guidedmodules.views.new_task),
]
