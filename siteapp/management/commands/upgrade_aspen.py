import sys
import os.path
import json
from uuid import uuid4

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization, Portfolio
from controls.models import Element
from controls.oscal import CatalogData
from django.contrib.auth.management.commands import createsuperuser
from siteapp.models import Role, Party, Appointment

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
            print("\n[INFO] - The database is not initialized yet.")
            sys.exit(1)

        # Add default start apps to organizations
        try:
            for org in Organization.objects.all():
                if "default_appversion_name_list" not in org.extra:
                    org.extra["default_appversion_name_list"] = [
                        "Blank Project",
                        "Speedy SSP",
                        "General IT System ATO for 800-53 (low)"
                    ]
                    org.save()
        except:
            print("\n[WARN] Problem adding default project templates to organization. Contact GovReady at info@govready.com.")

        print("Aspen related configuration upgrades complete.")
