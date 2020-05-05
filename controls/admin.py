from django.contrib import admin
from .models import Statement, Element, ElementControl, System, CommonControlProvider, CommonControl


class StatementAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'sid_class', 'parent')

class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'id')

class ElementControlAdmin(admin.ModelAdmin):
    list_display = ('id', 'element', 'oscal_ctl_id', 'oscal_catalog_key')

class SystemAdmin(admin.ModelAdmin):
    list_display = ('id', 'root_element')

class CommonControlProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

class CommonControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'oscal_ctl_id', 'id')


admin.site.register(Statement, StatementAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(ElementControl, ElementControlAdmin)
admin.site.register(System, SystemAdmin)
admin.site.register(CommonControlProvider, CommonControlProviderAdmin)
admin.site.register(CommonControl, CommonControlAdmin)

