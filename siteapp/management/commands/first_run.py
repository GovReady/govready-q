import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization, Portfolio
from controls.models import Element
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

        # Create the default organization.
        if not Organization.objects.all().exists() and not Organization.objects.filter(name="main").exists():
            org = Organization.objects.create(name="main", slug="main")

        # Install default AppSources and compliance apps if no AppSources installed
        if AppSource.objects.all().exists():
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
                for appname in ["blank", "speedyssp", "System-Description-Demo",
                                "PTA-Demo", "rules-of-behavior", "lightweight-ato", "lightweight-ato-800-171"]:
                    print("Adding appname '{}' from AppSource '{}' to catalog.".format(appname, created_appsource))
                    try:
                        appver = created_appsource.add_app_to_catalog(appname)
                    except Exception as e:
                        raise

            # Finally, for authoring, create an AppSource to the stub file
            qfiles_path = 'guidedmodules/stubs/q-files'
            if os.path.exists(qfiles_path):
                # For 0.9.x+.
                appsource, created = AppSource.objects.get_or_create(
                    slug="govready-q-files-stubs",
                    defaults={
                        "spec": { "type": "local", "path": qfiles_path }
                    }
                )
                if created:
                    print("Adding AppSource for authoring.")
                else:
                    print("Confirmed that AppSource for authoring exists.")
        else:
            print("AppSources exist. Skipping install of defaults AppSources.")

        # Install default example components if no components in library
        if len(Element.objects.all()) == 0:
            from controls.views import ComponentImporter
            path = 'q-files/vendors/govready/components/OSCAL'
            import_name = "Default components"
            if os.path.exists(path):
                for component_file in os.listdir(path):
                    # Read component json file as text
                    if component_file.endswith(".json"):
                        with open(os.path.join(path, component_file)) as f:
                            oscal_component_json = f.read()
                            result = ComponentImporter().import_components_as_json(import_name, oscal_component_json)

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
                    # Create the first portfolio
                    portfolio = user.create_default_portfolio_if_missing()
                    print("Created administrator portfolio {}".format(portfolio.title))
                else:
                    print("\n[INFO] Skipping create admin account '{}' - username already exists.\n".format(
                        username
                    ))

        # Create default users, if specified in local/environment.json otherwise read from SSM parameter store
        users = settings.GOVREADY_USERS
        if len(settings.GOVREADY_USERS):
            # TODO: iterate for each environment. Need to modularize this loop.
            for reg_user in users:
                username = reg_user["username"]
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create(username=username, is_superuser=False, is_staff=False)
                    user.set_password(reg_user["password"])
                    user.email = reg_user["email"]
                    user.save()
                    print("Created regular user account: username '{}' with email '{}'.".format(
                        user.username,
                        user.email
                    ))
                    # Create the first portfolio
                    portfolio = user.create_default_portfolio_if_missing()
                    print("Created regular user portfolio {}".format(portfolio.title))
                else:
                    print("\n[INFO] Skipping create account '{}' - username already exists.\n".format(
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
                password = User.objects.make_random_password(length=12)
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

            # Add the user to the org's help squad and reviewers lists.
            try:
                user
            except NameError:
                print("[INFO] Admin already added to Help Squad and Reviewers")
            else:
                if user not in org.help_squad.all(): org.help_squad.add(user)
                if user not in org.reviewers.all(): org.reviewers.add(user)
                print("[INFO] Admin added to Help Squad and Reviewers")

        else:
            # One or more superusers already exists
            print("\n[INFO] Superuser(s) already exists, not creating default admin superuser. Did you specify 'govready_admins' in 'local/environment.json'? Did you specify an admin or are you connecting to a persistent database?\n")

        # Provide feedback to user
        print("GovReady-Q configuration complete.")
