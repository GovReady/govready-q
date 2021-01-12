from django.conf.urls import include, url

from django.contrib import admin
from django.conf import settings
admin.autodiscover()

import controls.views
from . import views

from siteapp.settings import *

urlpatterns = [
    url(r'^test$', views.test),

    # Catalogs
    url(r'^$', views.catalogs),
    url(r'^catalogs$', views.catalogs),
    url(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),

    # Systems
    url(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/selected$', views.controls_selected, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/compare$', views.editor_compare, name="control_compare"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)$', views.editor, name="control_editor"),
    url(r'^editor_autocomplete/', views.EditorAutocomplete.as_view(), name="search_system_component"),
    url(r'^related_system_components/', views.RelatedComponentStatements.as_view(), name="related_system_components"),
    url(r'^(?P<system_id>.*)/components/add_system_component$', views.add_system_component, name="add_system_component"),
    url(r'^(?P<system_id>.*)/components/editor_autocomplete$',  views.EditorAutocomplete.as_view(), name="editor_autocomplete"),
    url(r'^statement_history/(?P<smt_id>.*)/$', views.statement_history, name="statement_history"),
    url(r'^restore_to/(?P<smt_id>.*)/(?P<history_id>.*)/$', views.restore_to_history, name="restore_to"),

    url(r'^smt/_save/$', views.save_smt),
    url(r'^smt/_delete/$', views.delete_smt),
    url(r'^smt/_update_smt_prototype/$', views.update_smt_prototype),

    # System Components/Elements
    url(r'^(?P<system_id>.*)/components/selected$', views.components_selected, name="components_selected"),
    url(r'^(?P<system_id>.*)/components/selected/export/opencontrol$', views.export_system_opencontrol, name="export_system_opencontrol"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/download/oscal/json$', 
        views.system_element_download_oscal_json, 
        name="system_element_download_oscal_json"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)$', views.system_element, name="system_element"),
    url(r'^(?P<system_id>.*)/controls/updated$', views.controls_updated, name="controls_updated"),

    # Component Library
    url(r'^components$', views.component_library, name="component_library"),
    url(r'^components/new$', views.new_element, name="new_element"),
    url(r'^components/(?P<element_id>.*)/_copy$', views.component_library_component_copy, name="component_library_component_copy"),
    url(r'^components/(?P<element_id>.*)$', views.component_library_component, name="component_library_component"),
    url(r'^import_component$', views.import_component, name="import_component"),
    url(r'^import_records$', views.import_records, name="import_records"),
    url(r'^import_records/(?P<import_record_id>.*)/details$', views.import_record_details, name="import_record_details"),
    url(r'^import_records/(?P<import_record_id>.*)/delete_confirm$', views.confirm_import_record_delete, name="confirm_import_record_delete"),
    url(r'^import_records/(?P<import_record_id>.*)/delete$', views.import_record_delete, name="import_record_delete"),

    # Elements
    url(r'^elements/(\d+)/__rename$', views.rename_element, name="rename_element"),

    # Controls
    url(r'^catalogs/(?P<catalog_key>.*)/group/(?P<g_id>.*)', views.group, name="control_group"),
    url(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)', views.control, name="control_info"),
    url(r'^api/controlsselect/', views.api_controls_select, name="api_controls_select"),

    # Baselines
    url(r'^(?P<system_id>.*)/controls/baseline/(?P<catalog_key>.*)/(?P<baseline_name>.*)/_assign$', views.assign_baseline, name="assign_baseline"),

    # Poams
    url(r'^(?P<system_id>.*)/poams$', views.poams_list, name="poams_list"),
    url(r'^(?P<system_id>.*)/poams/new$', views.new_poam, name="new_poam"),
    url(r'^(?P<system_id>.*)/poams/(?P<poam_id>.*)/edit$', views.edit_poam, name="edit_poam"),
    url(r'^(?P<system_id>.*)/poams/export/csv$', views.poam_export_csv, name="poam_export_csv"),
    url(r'^(?P<system_id>.*)/poams/export/xlsx$', views.poam_export_xlsx, name="poam_export_xlsx"),

    # Project
    url(r'^(?P<project_id>.*)/import', views.project_import, name="project_import"),
    url(r'^(?P<project_id>.*)/export', views.project_export, name="project_export"),
]
