from django.contrib import admin
from .models import CommonControlProvider, CommonControl


class CommonControlProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

class CommonControlAdmin(admin.ModelAdmin):
    list_display = ('name', 'oscal_ctl_id', 'id')


admin.site.register(CommonControlProvider, CommonControlProviderAdmin)
admin.site.register(CommonControl, CommonControlAdmin)
