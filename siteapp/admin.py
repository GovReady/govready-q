from django.contrib import admin

import django.contrib.auth.admin as contribauthadmin

from .models import User, Organization, Project, ProjectMembership

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

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('subdomain', 'name')

    def save_model(self, request, obj, form, change):
        was_new = not obj.id
        obj.save()
        if was_new:
            # When creating a new Organization, add the admin user to it
            # so that that user can then invite others.
            self.add_me_as_admin(request, Organization.objects.filter(id=obj.id))

            # And initialize the root Task.
            obj.get_organization_project().set_root_task("organization", request.user)

    def add_me_as_admin(self, request, queryset):
        for org in queryset:
            mb, isnew = ProjectMembership.objects.get_or_create(
                user=request.user,
                project=org.get_organization_project(),
                )

            from django.contrib import messages
            if isnew or not mb.is_admin:
                messages.add_message(request, messages.INFO, 'You are now an admin of %s.' % org)
            else:
                messages.add_message(request, messages.INFO, 'You were already an admin of %s.' % org)

            mb.is_admin = True
            mb.save()

    add_me_as_admin.short_description = "Add me as an administrator to the organization"

    actions = [add_me_as_admin]

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('organization', 'title', 'owner_domains', 'created')
    def owner_domains(self, obj):
        return obj.get_owner_domains()

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'is_admin', 'created')
    raw_id_fields = ('project', 'user',)

admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)

