import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, AppVersion, Module
from siteapp.models import User, Organization
from django.contrib.auth.management.commands import createsuperuser
from django.shortcuts import get_object_or_404


class Command(BaseCommand):
    help = 'Add starter assessments from govready-q-files-startpack.'

    def add_arguments(self, parser):
        parser.add_argument('--non-interactive', action='store_true')

    def handle(self, *args, **options):
        # Sanity check that the database is ready --- make sure the system
        # modules exist (since we need them before creating an Organization).
        try:
            if not Module.objects.filter(
                app__source__is_system_source=True, app__appname="organization",
                app__system_app=True, module_name="app").exists():
                raise OperationalError() # to trigger below
        except OperationalError:
            print("The database is not initialized yet.")
            sys.exit(1)

        # Create AppSources that we want.
        if os.path.exists("/mnt/apps"):
            # For our docker image.
            AppSource.objects.get_or_create(
                slug="host",
                defaults={
                    "spec": { "type": "local", "path": "/mnt/apps" }
                }
            )
        appsource = AppSource.objects.get_or_create(
            slug="govready-q-files-startpack",
            defaults={
                "spec": { "type": "git", "url": "https://github.com/GovReady/govready-q-files-startpack.git", "branch": "master", "path": "apps"}
            }
        )

        # Load the AppSource we created
        created_appsource = get_object_or_404(AppSource, slug="govready-q-files-startpack")

        # Load the AppSource's assessments (apps) we want
        # We will do some hard-coding here temporarily
        appname = "System-Description-Demo"
        print("Adding appname '{}' from AppSource '{}' to catalog.".format(appname, created_appsource))

        try:
            appver = created_appsource.add_app_to_catalog(appname)
        except Exception as e:
            raise

        # Provide feedback to user
        print("A set of starter assessments have been added to your GovReady-Q.")
