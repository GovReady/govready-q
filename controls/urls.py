from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from controls.models import Element
from siteapp.model_mixins.tags import TagView, build_tag_urls

admin.autodiscover()

from django.views.decorators.csrf import csrf_exempt

from controls import views

from siteapp.settings import *

urlpatterns = [
    # Docs
    url('doc/', include('django.contrib.admindocs.urls')),

    # Catalogs
    url(r'^$', views.catalogs),
    url(r'^catalogs$', views.catalogs),
    url(r'^catalogs/(?P<catalog_key>.*)/$', views.catalog),

    # Systems
    url(r'^(?P<system_id>.*)/controls/selected/export/xacta/xlsx$', views.controls_selected_export_xacta_xslx, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/selected/aspen$', views.controls_selected_aspen, name="controls_selected_aspen"),
    url(r'^(?P<system_id>.*)/controls/selected$', views.controls_selected, name="controls_selected"),
    url(r'^(?P<system_id>.*)/controls/add$', views.system_controls_add, name="system_controls_add"),
    url(r'^(?P<system_id>.*)/controls/remove/(?P<element_control_id>.*)$',  views.system_control_remove, name="system_control_remove"),
    
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)/compare$', views.editor_compare, name="control_compare"),
    url(r'^(?P<system_id>.*)/controls/catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)$', views.editor, name="control_editor"),
    url(r'^editor_autocomplete/', views.EditorAutocomplete.as_view(), name="search_system_component"),
    url(r'^related_system_components/', views.RelatedComponentStatements.as_view(), name="related_system_components"),
    url(r'^(?P<system_id>.*)/components/add_system_component$', views.add_system_component, name="add_system_component"),
    url(r'^(?P<system_id>.*)/components/proposal_message$', views.proposal_message, name="proposal_message"),
    url(r'^(?P<system_id>.*)/components/remove_proposal/(?P<proposal_id>.*)$', views.system_proposal_remove, name="system_proposal_remove"),

    url(r'^(?P<system_id>.*)/components/editor_autocomplete$',  views.EditorAutocomplete.as_view(), name="editor_autocomplete"),
    url(r'^(?P<system_id>.)/profile/oscal/json', views.system_profile_oscal_json, name="profile_oscal_json"),
    url(r'^statement_history/(?P<smt_id>.*)/$', views.statement_history, name="statement_history"),
    url(r'^restore_to/(?P<smt_id>.*)/(?P<history_id>.*)/$', views.restore_to_history, name="restore_to"),

    url(r'^(?P<system_id>.*)/aspen/summary/fake$', views.system_summary_1_aspen, name="system_summary_1"),
    url(r'^(?P<system_id>.*)/aspen/summary$', views.system_summary_aspen, name="system_summary"),
    url(r'^(?P<system_id>.*)/aspen/integrations$', views.system_integrations_aspen, name="system_integrations"),

    url(r'^new', views.create_system_from_string, name="create_system_from_string"),

    # Systems Assessment Results
    url(r'^(?P<system_id>.*)/assessments$', views.system_assessment_results_list, name="system_assessment_results_list"),
    url(r'^(?P<system_id>.*)/assessments/new/wazuh$', views.new_system_assessment_result_wazuh, name="new_system_assessment_result_wazuh"),
    url(r'^(?P<system_id>.*)/assessment/new$', views.manage_system_assessment_result, name="new_system_assessment_result"),
    url(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/view$', views.view_system_assessment_result_summary, name="view_system_assessment_result_summary"),
    url(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/edit$', views.manage_system_assessment_result, name="manage_system_assessment_result"),
    url(r'^(?P<system_id>.*)/sar/(?P<sar_id>.*)/history$', views.system_assessment_result_history, name="system_assessment_result_history"),

    # Systems Inventory and Deployments
    url(r'^(?P<system_id>.*)/aspen/deployments$', views.system_deployments_aspen, name="system_deployments_aspen"),
    url(r'^(?P<system_id>.*)/deployments$', views.system_deployments, name="system_deployments"),
    url(r'^(?P<system_id>.*)/deployment/new$', views.manage_system_deployment, name="new_system_deployment"),
    url(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/edit$', views.manage_system_deployment, name="manage_system_deployment"),
    url(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/inventory$', views.system_deployment_inventory, name="system_deployment_inventory"),
    url(r'^(?P<system_id>.*)/deployment/(?P<deployment_id>.*)/history$', views.deployment_history, name="deployment_history"),

    # Statements
    url(r'^smt/_save/$', views.save_smt),
    url(r'^smt/_delete/$', views.delete_smt),
    url(r'^smt/_update_smt_prototype/$', views.update_smt_prototype),

    # System Components/Elements
    url(r'^(?P<system_id>.*)/aspen/components/selected$', views.SelectedComponentsListAspen.as_view(), name="components_selected_aspen"),
    url(r'^(?P<system_id>.*)/components/selected$', views.SelectedComponentsList.as_view(), name="components_selected"),
    url(r'^(?P<system_id>.*)/components/selected/export/opencontrol$', views.export_system_opencontrol, name="export_system_opencontrol"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/download/oscal/json$',
        views.system_element_download_oscal_json,
        name="system_element_download_oscal_json"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/_remove$', views.system_element_remove, name="system_element_remove"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)/(?P<catalog_key>.*)/(?P<control_id>.*)$', views.system_element_control, name="system_element_control"),
    url(r'^(?P<system_id>.*)/components/(?P<element_id>.*)/proposal_message$', views.proposal_message, name="proposal_message"),
    url(r'^(?P<system_id>.*)/component/(?P<element_id>.*)$', views.system_element, name="system_element"),
    url(r'^(?P<system_id>.*)/controls/updated$', views.controls_updated, name="controls_updated"),

    # Component Library
    url(r'^components$', views.component_library, name="component_library"),
    url(r'^components/compare$', views.compare_components, name="compare_components"),
    url(r'^components/new$', views.new_element, name="new_element"),
    url(r'^components/(?P<element_id>.*)/edit_component_state$',  views.edit_component_state, name="edit_component_state"),
    url(r'^components/(?P<element_id>.*)/edit_component_type$',  views.edit_component_type, name="edit_component_type"),
    url(r'^components/(?P<element_id>.*)/_copy$', views.component_library_component_copy, name="component_library_component_copy"),
    url(r'^components/(?P<element_id>.*)$', views.component_library_component, name="component_library_component"),
    url(r'^import_component$', views.import_component, name="import_component"),
    url(r'^import_records$', views.import_records, name="import_records"),
    url(r'^import_records/(?P<import_record_id>.*)/details$', views.import_record_details, name="import_record_details"),
    url(r'^import_records/(?P<import_record_id>.*)/delete_confirm$', views.confirm_import_record_delete, name="confirm_import_record_delete"),
    url(r'^import_records/(?P<import_record_id>.*)/delete$', views.import_record_delete, name="import_record_delete"),

    # Elements
    url(r'^elements/(\d+)/__edit$', views.edit_element, name="edit_element"),
    url(r'^elements/(\d+)/__edit_access$', views.edit_element_access_management, name="edit_element_access_management"),
    *build_tag_urls(r"^elements/(\d+)/", model=Element),  # Tag Urls

    # Controls
    url(r'^catalogs/(?P<catalog_key>.*)/group/(?P<g_id>.*)', views.group, name="control_group"),
    url(r'^catalogs/(?P<catalog_key>.*)/control/(?P<cl_id>.*)', views.control, name="control_info"),
    url(r'^api/controlsselect/', views.api_controls_select, name="api_controls_select"),

    # System Security plan
    url(r'^(?P<system_id>.*)/export/oscal', views.OSCAL_ssp_export, name="ssp_export_oscal"),

    # Baselines
    url(r'^(?P<system_id>.*)/controls/baseline/(?P<catalog_key>.*)/(?P<baseline_name>.*)/_assign$', views.assign_baseline, name="assign_baseline"),

    # Poams
    url(r'^(?P<system_id>.*)/aspen/poams$', views.system_poams_aspen, name="system_poams_aspen"),
    url(r'^import-poams$', views.import_poams_xlsx, name="import_poams_xlsx"),

    url(r'^(?P<system_id>.*)/poams$', views.poams_list, name="poams_list"),
    url(r'^(?P<system_id>.*)/poams/new$', views.new_poam, name="new_poam"),
    url(r'^(?P<system_id>.*)/poams/(?P<poam_id>.*)/edit$', views.edit_poam, name="edit_poam"),
    url(r'^(?P<system_id>.*)/poams/export/csv$', views.poam_export_csv, name="poam_export_csv"),
    url(r'^(?P<system_id>.*)/poams/export/xlsx$', views.poam_export_xlsx, name="poam_export_xlsx"),

    # Project
    url(r'^(?P<project_id>.*)/import', views.project_import, name="project_import"),
    url(r'^(?P<project_id>.*)/export', views.project_export, name="project_export"),
]
