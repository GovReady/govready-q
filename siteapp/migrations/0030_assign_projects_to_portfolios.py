# Generated by Django 2.0.13 on 2019-08-12 19:07

from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from guardian.shortcuts import assign_perm, get_perms_for_model


def assign_project_editor_permissions(apps, project, user):
    User = apps.get_model('siteapp', 'User')
    UserObjectPermission = apps.get_model('guardian', 'UserObjectPermission')
    Permission = apps.get_model('auth', 'Permission')
    project_type = ContentType.objects.get(
        app_label='siteapp', model='project')
    view_project, created = Permission.objects.get_or_create(codename='view_project', content_type_id=project_type.id)
    change_project, created = Permission.objects.get_or_create(codename='change_project', content_type_id=project_type.id)
    add_project, created = Permission.objects.get_or_create(codename='add_project', content_type_id=project_type.id)
    user_lookup = User.objects.get(id=user.id)
    permissions = [view_project, change_project, add_project]
    for perm in permissions:
        UserObjectPermission.objects.get_or_create(
            permission=perm, user=user_lookup, object_pk=project.pk, content_type_id=project_type.id)


def assign_project_owner_permissions(apps, project, user):
    User = apps.get_model('siteapp', 'User')
    UserObjectPermission = apps.get_model('guardian', 'UserObjectPermission')
    Permission = apps.get_model('auth', 'Permission')
    project_type = ContentType.objects.get(
        app_label='siteapp', model='project')
    view_project, created = Permission.objects.get_or_create(codename='view_project', content_type_id=project_type.id)
    change_project, created = Permission.objects.get_or_create(codename='change_project', content_type_id=project_type.id)
    add_project, created = Permission.objects.get_or_create(codename='add_project', content_type_id=project_type.id)
    delete_project, created = Permission.objects.get_or_create(codename='delete_project', content_type_id=project_type.id)
    permissions = [view_project, change_project, add_project, delete_project]
    user_lookup = User.objects.get(id=user.id)
    for perm in permissions:
        UserObjectPermission.objects.get_or_create(
            permission=perm, user=user_lookup, object_pk=project.pk, content_type_id=project_type.id)

def assign_portfolio_owner_permissions(apps, portfolio, user):
    User = apps.get_model('siteapp', 'User')
    UserObjectPermission = apps.get_model('guardian', 'UserObjectPermission')
    Permission = apps.get_model('auth', 'Permission')
    portfolio_type = ContentType.objects.get(app_label='siteapp', model='portfolio')
    portfolio_owner, created = Permission.objects.get_or_create(codename='can_grant_portfolio_owner_permission', content_type_id=portfolio_type.id)
    view_portfolio, created = Permission.objects.get_or_create(codename='view_portfolio', content_type_id=portfolio_type.id)
    change_portfolio, created = Permission.objects.get_or_create(codename='change_portfolio', content_type_id=portfolio_type.id)
    add_portfolio, created = Permission.objects.get_or_create(codename='add_portfolio', content_type_id=portfolio_type.id)
    delete_portfolio, created = Permission.objects.get_or_create(codename='delete_portfolio', content_type_id=portfolio_type.id)
    permissions = [portfolio_owner, view_portfolio, change_portfolio, add_portfolio, delete_portfolio]
    user_lookup = User.objects.get(id=user.id)
    for perm in permissions:
        print(portfolio)
        UserObjectPermission.objects.get_or_create(
            permission=perm, user=user_lookup, object_pk=portfolio.pk, content_type_id=portfolio_type.id)

def forwards(apps, schema_editor):
    Portfolio = apps.get_model('siteapp', 'Portfolio')
    Project = apps.get_model('siteapp', 'Project')
    User = apps.get_model('siteapp', 'User')
    ProjectMembership = apps.get_model('siteapp', 'ProjectMembership')

    projects = Project.objects.all()
    users = User.objects.all()

    for user in users:
        portfolio, created = Portfolio.objects.get_or_create(title=user.username)
        assign_portfolio_owner_permissions(apps, portfolio, user)

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
            assign_project_editor_permissions(apps, project, pm.user)
            if pm.is_admin:
                # if admin assign owner permissions
                assign_project_owner_permissions(apps, project, pm.user)
                if project.portfolio:
                    assign_portfolio_owner_permissions(apps, project.portfolio, pm.user)


class Migration(migrations.Migration):

    dependencies = [
        ('siteapp', '0029_auto_20190801_2000'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
