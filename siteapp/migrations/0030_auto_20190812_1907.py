# Generated by Django 2.0.13 on 2019-08-12 19:07

import logging

from django.db import migrations
from guardian.shortcuts import assign_perm, get_perms_for_model
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


def assign_editor_permissions(apps, model, user):
    User = apps.get_model('siteapp', 'User')
    UserObjectPermission = apps.get_model('guardian', 'UserObjectPermission')
    Permission = apps.get_model('auth', 'Permission')
    project_type = ContentType.objects.get(app_label='siteapp', model='project')
    view_project = Permission.objects.get(codename='view_project')
    change_project = Permission.objects.get(codename='change_project')
    add_project = Permission.objects.get(codename='add_project')
    user_lookup = User.objects.get(id=user.id)
    permissions = [view_project, change_project, add_project]
    for perm in permissions:
        UserObjectPermission.objects.create(permission=perm, user=user_lookup, content_type_id=project_type.id)


def assign_owner_permissions(apps, model, user):
    User = apps.get_model('siteapp', 'User')
    UserObjectPermission = apps.get_model('guardian', 'UserObjectPermission')
    Permission = apps.get_model('auth', 'Permission')
    project_type = ContentType.objects.get(app_label='siteapp', model='project')
    view_project = Permission.objects.get(codename='view_project')
    change_project = Permission.objects.get(codename='change_project')
    add_project = Permission.objects.get(codename='add_project')
    permissions = [view_project, change_project, add_project]
    user_lookup = User.objects.get(id=user.id)
    for perm in permissions:
        UserObjectPermission.objects.create(permission=perm, user=user_lookup, content_type_id=project_type.id)

def forwards(apps, schema_editor):
    Portfolio = apps.get_model('siteapp', 'Portfolio')
    Project = apps.get_model('siteapp', 'Project')
    ProjectMembership = apps.get_model('siteapp', 'ProjectMembership')

    projects = Project.objects.all()

    for project in projects:
        if project.organization and project.portfolio is None:
            # get or create portfolio from project organization
            portfolio, created = Portfolio.objects.get_or_create(
                title=project.organization.name)
            # assign projects portfolio id
            project.portfolio = portfolio
            # save project
            project.save()

        # get project membership object
        project_memberships = ProjectMembership.objects.filter(project=project)
        for pm in project_memberships:
            # assign editor permissions
            logger.info("assigning editor permission for {} to {}".format(pm.project, pm.user))
            assign_editor_permissions(apps, project, pm.user)
            if pm.is_admin:
                # if admin assign owner permissions
                logger.info("assigning owner permission for {} to {}".format(pm.project, pm.user))
                assign_owner_permissions(apps, project, pm.user)

    # TODO
    # what to do with project.is_account_project?
    # what to do with project.is_organization_project?


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0029_auto_20190801_2000'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
