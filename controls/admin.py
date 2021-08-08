import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import ImportRecord, Statement, Element, ElementControl, ElementRole, System, CommonControlProvider, CommonControl, ElementCommonControl, Poam, Deployment, SystemAssessmentResult
from .oscal import CatalogData
from guardian.admin import GuardedModelAdmin
from simple_history.admin import SimpleHistoryAdmin

class ExportCsvMixin:
    # From https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected as CSV"

class ImportRecordAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('created', 'uuid')
    actions = ["export_as_csv"]

class StatementAdmin(SimpleHistoryAdmin, ExportCsvMixin):
    list_display = ('id', 'sid', 'sid_class', 'producer_element', 'statement_type', 'uuid')
    search_fields = ('id', 'sid', 'sid_class', 'producer_element', 'uuid')
    actions = ["export_as_csv"]
    readonly_fields = ('created', 'updated', 'uuid')

class ElementAdmin(GuardedModelAdmin, ExportCsvMixin):
    list_display = ('name', 'full_name', 'element_type', 'id', 'uuid')
    search_fields = ('name', 'full_name', 'uuid', 'id')
    actions = ["export_as_csv"]

class ElementControlAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'element', 'oscal_ctl_id', 'oscal_catalog_key')
    actions = ["export_as_csv"]
    readonly_fields = ('created', 'updated', 'smts_updated')

class ElementRoleAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'role', 'description')
    search_fields = ('role', 'description')
    actions = ["export_as_csv"]
    readonly_fields = ('created', 'updated')

class SystemAdmin(GuardedModelAdmin, ExportCsvMixin):
    list_display = ('id', 'root_element')
    actions = ["export_as_csv"]

class CommonControlProviderAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'id')
    actions = ["export_as_csv"]

class CommonControlAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'oscal_ctl_id', 'id')
    actions = ["export_as_csv"]

class ElementCommonControlAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('element', 'common_control', 'oscal_ctl_id', 'id')
    actions = ["export_as_csv"]

class PoamAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'poam_id', 'statement', 'controls', 'uuid')
    search_fields = ('id', 'poam_id', 'statement', 'controls', 'uuid')
    actions = ["export_as_csv"]

    def uuid(self, obj):
        return obj.statement.uuid

    def consumer_element(self, obj):
        return obj.statement.consumer_element

class DeploymentAdmin(SimpleHistoryAdmin, ExportCsvMixin):
    list_display = ('id', 'name', 'system')
    search_fields = ('id', 'name', 'uuid')
    actions = ["export_as_csv"]

    def uuid(self, obj):
        return obj.deployment.uuid

class SystemAssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'system', 'deployment', 'uuid')
    search_fields = ('id', 'name', 'system', 'deployment', 'uuid')

class CatalogDataAdmin(admin.ModelAdmin):
    list_display = ('catalog_key',)
    search_fields = ('catalog_key',)

admin.site.register(ImportRecord, ImportRecordAdmin)
admin.site.register(Statement, StatementAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(ElementControl, ElementControlAdmin)
admin.site.register(ElementRole, ElementRoleAdmin)
admin.site.register(System, SystemAdmin)
admin.site.register(CommonControlProvider, CommonControlProviderAdmin)
admin.site.register(CommonControl, CommonControlAdmin)
admin.site.register(ElementCommonControl, ElementCommonControlAdmin)
admin.site.register(Poam, PoamAdmin)
admin.site.register(Deployment, DeploymentAdmin)
admin.site.register(SystemAssessmentResult, SystemAssessmentResultAdmin)
admin.site.register(CatalogData, CatalogDataAdmin)
