from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import guidedmodules.views

urlpatterns = [

    # multi-question authoring tool
    url(r'^module/(\d+)/questions$', guidedmodules.views.show_module_questions, name="show_module_questions"),
    url(r'^_authoring_tool/edit-question2$', guidedmodules.views.authoring_edit_question2),
    url(r'^module/(\d+)/artifact/new$', guidedmodules.views.add_module_artifact, name="add_module_artifact"),
    url(r'^module/(\d+)/artifact/([\w_-]+)$', guidedmodules.views.show_module_artifact, name="show_module_artifact"),
    url(r'^_authoring_tool/edit-artifact$', guidedmodules.views.authoring_edit_artifact, name="authoring_edit_artifact"),

    # question management urls
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
    url(r'^_authoring_tool/new-question2$', guidedmodules.views.authoring_new_question2),
    url(r'^_authoring_tool/edit-module$', guidedmodules.views.authoring_edit_module),
    url(r'^_authoring_tool/create-app-project$', guidedmodules.views.authoring_create_q),
    url(r'^_authoring_tool/import-appsource$', guidedmodules.views.authoring_import_appsource),
    url(r'^_authoring_tool/edit-appversion$', guidedmodules.views.authoring_edit_appversion, name="authoring_edit_appversion"),
    url(r'^_upgrade-app$', guidedmodules.views.upgrade_app),
    url(r'^_refresh-output-doc$', guidedmodules.views.refresh_output_doc),
]

