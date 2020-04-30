import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Statement, Element, ElementControl, System, CommonControlProvider, CommonControl
from guardian.admin import GuardedModelAdmin

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

class StatementAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'sid', 'sid_class', 'parent')
    actions = ["export_as_csv"]

class ElementAdmin(GuardedModelAdmin, ExportCsvMixin):
    list_display = ('name', 'full_name', 'id')
    actions = ["export_as_csv"]

class ElementControlAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'element', 'oscal_ctl_id', 'oscal_catalog_key')
    actions = ["export_as_csv"]

class SystemAdmin(GuardedModelAdmin, ExportCsvMixin):
    list_display = ('id', 'root_element')
    actions = ["export_as_csv"]

class CommonControlProviderAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'id')
    actions = ["export_as_csv"]

class CommonControlAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'oscal_ctl_id', 'id')
    actions = ["export_as_csv"]


admin.site.register(Statement, StatementAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(ElementControl, ElementControlAdmin)
admin.site.register(System, SystemAdmin)
admin.site.register(CommonControlProvider, CommonControlProviderAdmin)
admin.site.register(CommonControl, CommonControlAdmin)

