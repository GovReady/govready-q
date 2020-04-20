from django.contrib import admin
from .models import Statement, Element, CommonControlProvider, CommonControl


class StatementAdmin(admin.ModelAdmin):
    list_display = ('sid', 'sid_class', 'parent', 'id')

class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'id')

class CommonControlProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

class CommonControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'oscal_ctl_id', 'id')


admin.site.register(Statement, StatementAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(CommonControlProvider, CommonControlProviderAdmin)
admin.site.register(CommonControl, CommonControlAdmin)