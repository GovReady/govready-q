import sys

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization
from django.contrib.auth.management.commands import createsuperuser

class Command(BaseCommand):
    help = 'Interactively set up an initial user and organization.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Sanity check that the database is ready --- make sure the system
        # modules exist (since we need them before creating an Organization).
        try:
            if not Module.objects.filter(
                app__source__namespace="system", app__appname="organization",
                app__system_app=True, module_name="app").exists():
                raise OperationalError() # to trigger below
        except OperationalError:
            # deployment/docker/first_run.sh expects a non-zero exit code here
            # and no output.
            sys.exit(1)

        # Create AppSources that we want.
        AppSource.objects.get_or_create(
            namespace="host",
            defaults={
                "spec": { "type": "local", "path": "/mnt/apps" }
            }
        )
        AppSource.objects.get_or_create(
            namespace="samples",
            defaults={
                "spec": { "type": "git", "url": "https://github.com/GovReady/govready-sample-apps" }
            }
        )

        # Create the first user.
        if not User.objects.filter(is_superuser=True).exists():
            print("Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.")
            call_command('createsuperuser')

        # Create the first organization.
        if not Organization.objects.exists():
            print("Let's create your Q organization.")
            name = Organization._meta.get_field("name")
            get_input = createsuperuser.Command().get_input_data
            
            name = get_input(name, "Organization Name: ", "Test Organization")
            
            org = Organization.create(name=name, subdomain="main", admin_user=User.objects.filter(is_superuser=True).first())
