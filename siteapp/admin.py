from django.contrib import admin
from django.contrib.auth.models import Permission
from guardian.admin import GuardedModelAdmin

import django.contrib.auth.admin as contribauthadmin

from .models import User, Organization, OrganizationalSetting, Folder, Project, ProjectMembership, Portfolio, Support
from notifications.models import Notification

def all_user_fields_still_exist(fieldlist):
    for f in fieldlist:
        try:
            User._meta.get_field(f)
        except:
            return False
    return True

def add_viewappsource_permission(modeladmin, request, queryset):
    """
    Adds view appsource permission to selected users
    """
    for user in queryset:
        # Adds permission if they dont the permission
        if 'guidedmodules.view_appsource' not in user.get_user_permissions():
            user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
add_viewappsource_permission.short_description = "Add View Appsource permission to selected users."

class UserAdmin(contribauthadmin.UserAdmin):
    ordering = ('username',)
    list_display = ('id', 'email', 'date_joined', 'notifemails_enabled', 'notifemails_last_notif_id') # base has first_name, etc. fields that we don't have on our model
    actions = [add_viewappsource_permission]
    pass

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'id')
    filter_horizontal = ('help_squad', 'reviewers')

    def save_model(self, request, obj, form, change):
        was_new = not obj.id
        obj.save()
        if was_new:
            # When creating a new Organization, add the admin user to it
            # so that that user can then invite others.
            self.add_me_as_admin(request, Organization.objects.filter(id=obj.id))

            # And initialize the root Task. See Organization.create.
            obj.get_organization_project().set_system_task("organization", request.user)

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

        # Create a random pwd for any new test accounts that are
        # created. Use the same pwd for all.
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

    add_me_as_admin.short_description = "Add me as an administrator to the organization"
    populate_test_organization.short_description = "Populate with the test users"

    actions = [add_me_as_admin, populate_test_organization]

class OrganizationalSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'catalog_key', 'parameter_key', 'value')
    readonly_fields = ('id',)

class FolderAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    raw_id_fields = ('organization','admin_users')
    readonly_fields = ('projects', 'extra')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'actor', 'level', 'target', 'unread', 'public', 'emailed')
    readonly_fields = ('id',)

class ProjectAdmin(GuardedModelAdmin):
    list_display = ('id', 'portfolio_name', 'organization_name', 'title', 'root_task', 'created')
    raw_id_fields = ('root_task',)
    readonly_fields = ('id', 'extra',)

    def portfolio_name(self, obj):
        if obj.portfolio:
            return obj.portfolio.title

    portfolio_name.admin_order_field = 'portfolio'

    def organization_name(self, obj):
        if obj.organization:
            return obj.organization.name

    organization_name.admin_order_field = 'organization'

class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'organization', 'user', 'is_admin', 'created')
    raw_id_fields = ('project', 'user',)
    def organization(self, obj):
        return obj.project.organization

class PortfolioAdmin(GuardedModelAdmin):
    list_display = ('title', 'description')
    fields = ('title', 'description')

class SupportAdmin(admin.ModelAdmin):
  list_display = ('id', 'email',)
  fields = ('text', 'email', 'phone', 'url')

admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationalSetting, OrganizationalSettingAdmin)

admin.site.register(Folder, FolderAdmin)

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
# Notification is an external library and registers itself. So we need to unregister and re-register it.
admin.site.unregister(Notification)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Support, SupportAdmin)

