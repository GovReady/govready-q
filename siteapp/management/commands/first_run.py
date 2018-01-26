import sys
import os.path

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
        AppSource.objects.get_or_create(
            slug="samples",
            defaults={
                "spec": { "type": "git", "url": "https://github.com/GovReady/govready-sample-apps" }
            }
        )

        # Create the first user.
        if not User.objects.filter(is_superuser=True).exists():
            if not options['non_interactive']:
                print("Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.")
                call_command('createsuperuser')
            else:
                # Create an "admin" account with a random password and
                # print it on stdout.
                user = User.objects.create(username="admin", is_superuser=True, is_staff=True)
                password = User.objects.make_random_password(length=24)
                user.set_password(password)
                user.save()
                print("Created administrator account (username: {}) with password: {}".format(
                    user.username,
                    password
                ))

        # Get the admin user - it was just created and should be the only admin user.
        user = User.objects.filter(is_superuser=True).get()

        # Create the first organization.
        if not Organization.objects.filter(subdomain="main").exists():
            if not options['non_interactive']:
                print("Let's create your Q organization.")
                name = Organization._meta.get_field("name")
                get_input = createsuperuser.Command().get_input_data
                
                name = get_input(name, "Organization Name: ", "Test Organization")
            else:
                name = "The Secure Company"
            org = Organization.create(name=name, subdomain="main", admin_user=user)
        else:
            org = Organization.objects.get(subdomain="main")

        # Add the user to the org's help squad and reviewers lists.
        if user not in org.help_squad.all(): org.help_squad.add(user)
        if user not in org.reviewers.all(): org.reviewers.add(user)
