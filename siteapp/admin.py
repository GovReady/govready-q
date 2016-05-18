from django.contrib import admin

import django.contrib.auth.admin as contribauthadmin

from .models import User, Project, ProjectMembership

def all_user_fields_still_exist(fieldlist):
    for f in fieldlist:
        try:
            User._meta.get_field(f)
        except:
            return False
    return True

class UserAdmin(contribauthadmin.UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'id', 'date_joined') # base has first_name, etc. fields that we don't have on our model
    fieldsets = [
        (None, {'fields': ('email', 'password')}),
    ] + [fs for fs in contribauthadmin.UserAdmin.fieldsets if all_user_fields_still_exist(fs[1]['fields'])]

    pass

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner_domains', 'created')
    def owner_domains(self, obj):
        return obj.get_owner_domains()

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'is_admin', 'created')
    raw_id_fields = ('project', 'user',)

admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)

