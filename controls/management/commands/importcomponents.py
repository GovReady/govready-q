import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings
from pathlib import Path
from pathlib import PurePath
from django.utils.text import slugify

# from siteapp.models import User, Organization, Portfolio
from controls.models import Element, Statement
# from controls.views import system_element_download_oscal_json
from controls.views import OSCALComponentSerializer, ComponentImporter

import fs, fs.errors


class Command(BaseCommand):
    help = 'Import directory of component files.'

    def add_arguments(self, parser):
        parser.add_argument('--format', metavar='format', nargs='?', default="oscal", help="File format")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', default="local/export/components", help="The directory path containing component files to import.")
        parser.add_argument('--importname', metavar='importname', nargs='?', default="Batch component import", help="Name to identify the batch import")
        parser.add_argument('--stopinvalid', default=True, action='store_true')
        parser.add_argument('--no-stopinvalid', dest='stopinvalid', action='store_false')


    def handle(self, *args, **options):

        # Configure
        FORMAT = options['format']
        IMPORT_PATH = options['path']
        IMPORT_NAME = options['importname']
        STOPINVALID = options['stopinvalid']
        # Check if import directory path exists
        if not os.path.exists(IMPORT_PATH):
            print(f"Import directory {IMPORT_PATH} not found.")
            quit()

        if FORMAT == 'oscal':
            counter = 0
            # Get list of files in directory
            pathlist = Path(IMPORT_PATH).rglob('*.json')
            print(pathlist)
            # Import each file
            for path in pathlist:
                counter += 1
                path_in_str = str(path)
                print(path_in_str)

                with open(path_in_str) as f:
                    oscal_component_json = f.read()
                    result = ComponentImporter().import_components_as_json(IMPORT_NAME, oscal_component_json, existing_import_record=True, stopinvalid=STOPINVALID)

        elif FORMAT == "csv":
            import csv
            counter = 0
            print(f"Format '{FORMAT}' not yet supported.")
        else:
            print(f"Format '{FORMAT}' not yet supported.")

        # Done
        print(f"Imported {counter} components in {FORMAT} from folder `{IMPORT_PATH}`.")

