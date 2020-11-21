import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization, Portfolio
from django.contrib.auth.management.commands import createsuperuser

import fs, fs.errors


class Command(BaseCommand):
    help = 'Interactively set up an initial user and organization.'

    def add_arguments(self, parser):
        parser.add_argument('--non-interactive', action='store_true')

    def handle(self, *args, **options):
        # Sanity check that the database is available and ready --- make sure the system
        # modules exist (since we need them before creating an Organization).
        # Also useful in container deployments to make sure container fully deployed.
        try:
            if not Module.objects.filter(
                app__source__is_system_source=True, app__appname="organization",
                app__system_app=True, module_name="app").exists():
                raise OperationalError() # to trigger below
        except OperationalError:
            print("The database is not initialized yet.")
            sys.exit(1)

        # Create AppSources that we want.
        if os.path.exists("/mnt/q-files-host"):
            # For our docker image.
            AppSource.objects.get_or_create(
                slug="host",
                defaults={
                    "spec": { "type": "local", "path": "/mnt/q-files-host" }
                }
            )
        # Second, for 0.9.x startpack
        # We can use forward slashes because we are storing the path in the database
        # and the path will be applied correctly to the operating OS.
        qfiles_path = 'q-files/vendors/govready/govready-q-files-startpack/q-files'
        if os.path.exists(qfiles_path):
            # For 0.9.x+.
            AppSource.objects.get_or_create(
                slug="govready-q-files-startpack",
                defaults={
                    "spec": { "type": "local", "path": qfiles_path }
                }
            )
            # Load the AppSource's assessments (apps) we want
            # We will do some hard-coding here temporarily
            created_appsource = AppSource.objects.get(slug="govready-q-files-startpack")
            for appname in ["System-Description-Demo", "PTA-Demo", "rules-of-behavior"]:
                print("Adding appname '{}' from AppSource '{}' to catalog.".format(appname, created_appsource))
                try:
                    appver = created_appsource.add_app_to_catalog(appname)
                except Exception as e:
                    raise

        # Finally, for authoring, create an AppSource to the stub file
        qfiles_path = 'guidedmodules/stubs/q-files'
        if os.path.exists(qfiles_path):
            # For 0.9.x+.
            AppSource.objects.get_or_create(
                slug="govready-q-files-stubs",
                defaults={
                    "spec": { "type": "local", "path": qfiles_path }
                }
            )
            print("Adding AppSource for authoring.")

        # Create GovReady admin users, if specified in local/environment.json
        if len(settings.GOVREADY_ADMINS):
            for admin_user in settings.GOVREADY_ADMINS:
                username = admin_user["username"]
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create(username=username, is_superuser=True, is_staff=True)
                    user.set_password(admin_user["password"])
                    user.email = admin_user["email"]
                    user.save()
                    print("Created administrator account: username '{}' with email '{}'.".format(
                        user.username,
                        user.email
                    ))
                else:
                    print("\n[WARNING] Skipping create admin account '{}' - username already exists.\n".format(
                        username
                    ))

        # Create the first user.
        if not User.objects.filter(is_superuser=True).exists():
            if not options['non_interactive']:
                print("Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.")
                call_command('createsuperuser')
            else:
                # Create an "admin" account with a random pwd and
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

            # Create the first portfolio
            portfolio = Portfolio.objects.create(title=user.username)
            portfolio.assign_owner_permissions(user)
            print("Created administrator portfolio {}".format(portfolio.title))
        else:
            # One or more superusers already exist
            print("\n[WARNING] Superuser(s) already exist, not creating default admin superuser. Did you specify 'govready_admins' in 'local/environment.json'? Are you connecting to a persistent database?\n")

        # Create the first organization.
        if not Organization.objects.filter(slug="main").exists():
            if not options['non_interactive']:
                print("Let's create your organization.")
                name = Organization._meta.get_field("name")
                get_input = createsuperuser.Command().get_input_data
                
                name = get_input(name, "Organization name: ", "My Organization")
            else:
                name = "The Secure Organization"
            org = Organization.create(name=name, slug="main", admin_user=user)
        else:
            org = Organization.objects.get(slug="main")

        # Add the user to the org's help squad and reviewers lists.
        try:
            user
        except NameError:
            print("[WARNING] Admin already added to Help Squad and Reviewers")
        else:
            if user not in org.help_squad.all(): org.help_squad.add(user)
            if user not in org.reviewers.all(): org.reviewers.add(user)

        # Provide feedback to user
        print("You can now login into GovReady-Q...")
