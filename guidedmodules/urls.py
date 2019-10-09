from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [
    url(r'^(\d+)/([\w_-]+)(/_save)()$', guidedmodules.views.save_answer),
    url(r'^(\d+)/([\w_-]+)(/question/)([\w_-]+)$', guidedmodules.views.show_question),
    url(r'^(\d+)/([\w_-]+)(/question/)([\w_-]+)/history/(\d+)/media$', guidedmodules.views.download_answer_file),
    url(r'^(\d+)/([\w_-]+)(/finished)()$', guidedmodules.views.task_finished),
    url(r'^(\d+)/([\w_-]+)/media/(.*)$', guidedmodules.views.download_module_asset),
    url(r'^(\d+)/([\w_-]+)/(download/document)()/(.*)/(.*)$', guidedmodules.views.download_module_output),
    url(r'^(\d+)/([\w_-]+)()()$', guidedmodules.views.next_question),
    url(r'^start$', guidedmodules.views.new_task),
    url(r'^_delete_task$', guidedmodules.views.delete_task, name="delete_task"),
    url(r'^_get_task_timetamp$', guidedmodules.views.get_task_timetamp, name="task_get_timestamp"),
    url(r'^_instrumentation_record_interaction$', guidedmodules.views.instrumentation_record_interaction, name="task_instrumentation_record_interaction"),
    url(r'^_start_discussion', guidedmodules.views.start_a_discussion, name="start_a_discussion"),
    url(r'^analytics$', guidedmodules.views.analytics, name="guidedmodules_analytics"),
    url(r'^_authoring_tool/new-question$', guidedmodules.views.authoring_new_question),
    url(r'^_authoring_tool/edit-question$', guidedmodules.views.authoring_edit_question),
    url(r'^_authoring_tool/edit-module$', guidedmodules.views.authoring_edit_module),
    url(r'^_authoring_tool/download-app$', guidedmodules.views.authoring_download_app),
    url(r'^_authoring_tool/create-app-project$', guidedmodules.views.authoring_create_q),
    url(r'^_authoring_tool/download-app-project$', guidedmodules.views.authoring_download_app_project),
    url(r'^_upgrade-app$', guidedmodules.views.upgrade_app),
]

