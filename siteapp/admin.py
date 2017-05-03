from django.contrib import admin

import django.contrib.auth.admin as contribauthadmin

from .models import User, Organization, Folder, Project, ProjectMembership

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

            # And initialize the root Task. See Organization.create.
            obj.get_organization_project().set_root_task("system/organization/app", request.user)

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

    def populate_test_organization(self, request, queryset):
        # Add me as an admin to the org and add our hard-coded
        # test accounts to the org, and pre-fill everybodies
        # org profile info based on the last profile info that
        # each user made in any other organization. Create the
        # users if they don't already exist - for firt time runs
        # and on dev machines.

        from django.contrib import messages
        from django.utils.crypto import get_random_string

        # Create a random password for any new test accounts that are
        # created. Use the same password for all.
        pw = get_random_string(12, 'abcdefghkmnpqrstuvwxyz23456789')

        for org in queryset:
            for user in (
                "SELF",
                "oscar.goldman", "steve.austin", "jaime.sommers", "bigfoot"):

                # Get or create user.
                if user == "SELF":
                    user = request.user
                else:
                    user, is_new = User.objects.get_or_create(username=user, email=user+"@osi.group")
                    if is_new:
                        user.set_password(pw)
                        user.save()
                        messages.add_message(request, messages.INFO, 'Create user %s with password %s.' % (user.username, pw))

                # Add user as an admin to the organization.
                mb, isnew = ProjectMembership.objects.get_or_create(
                    user=user,
                    project=org.get_organization_project(),
                    )
                if isnew or not mb.is_admin:
                    messages.add_message(request, messages.INFO, '%s was added as an administrator to %s.' % (user, org))
                mb.is_admin = True
                mb.save()

                # Copy forward profile info from the last time the user
                # entered any profile info.
                prev_profile = Project.objects\
                    .filter(
                        is_account_project=True,
                        members__user=user,
                        )\
                    .exclude(organization=org)\
                    .order_by('-created')\
                    .first()
                if prev_profile:
                    prev_profile_task = prev_profile.root_task.get_or_create_subtask(user, "account_settings")
                    if prev_profile_task.get_answers().as_dict(): # not empty
                        prev_profile_json = prev_profile.export_json()
                        new_profile = user.get_account_project_(org)
                        new_profile.import_json(prev_profile_json, user, lambda msg : print(msg))

    add_me_as_admin.short_description = "Add me as an administrator to the organization"
    populate_test_organization.short_description = "Populate with the test users"

    actions = [add_me_as_admin, populate_test_organization]

class FolderAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    raw_id_fields = ('organization','admin_users')
    readonly_fields = ('projects', 'extra')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'root_task', 'created')
    raw_id_fields = ('organization', 'root_task')
    readonly_fields = ('extra',)
    def project(self, obj):
        return obj.organization_and_title()

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'organization', 'user', 'is_admin', 'created')
    raw_id_fields = ('project', 'user',)
    def organization(self, obj):
        return obj.project.organization

admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)

