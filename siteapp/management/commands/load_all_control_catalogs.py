import os.path
import json
import sys

from controls.models import Element
from controls.oscal import CatalogData

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
#from django.db.utils import OperationalError
#from django.conf import settings

class Command(BaseCommand):
    help = 'Load Control Catalog into Database'

    def add_arguments(self, parser):
        parser.add_argument('--username', nargs='?')
        parser.add_argument('--catalog_key', nargs='?')
        parser.add_argument('--catalog_file', nargs='?')
        parser.add_argument('--baseline', nargs='?')
        parser.add_argument('--debug', nargs='?')

    @transaction.atomic
    def handle(self, *args, **options):
        """Load control catalog data into database"""

        # Load the default control catalogs and baselines
        CATALOG_PATH = os.path.join(os.path.dirname(__file__),'..','..','..','controls','data','catalogs')
        BASELINE_PATH = os.path.join(os.path.dirname(__file__),'..','..','..','controls','data','baselines')

        # TODO: Check directory exists
        catalog_files = [file for file in os.listdir(CATALOG_PATH) if file.endswith('.json')]
        # Load catalog and baseline data into database records from source files if data records do not exist in database
        for cf in catalog_files:
            catalog_key = cf.replace("_catalog.json", "")
            with open(os.path.join(CATALOG_PATH,cf), 'r') as json_file:
                catalog_json = json.load(json_file)
            baseline_filename = cf.replace("_catalog.json", "_baselines.json")
            if os.path.isfile(os.path.join(BASELINE_PATH, baseline_filename)):
                with open(os.path.join(BASELINE_PATH, baseline_filename), 'r') as json_file:
                    baselines_json = json.load(json_file)
            else:
                baselines_json = {}

            catalog, created = CatalogData.objects.get_or_create(
                    catalog_key=catalog_key,
                    catalog_json=catalog_json,
                    baselines_json=baselines_json
                )
            if created:
                print(f"{catalog_key} record created into database")
            else:
                print(f"{catalog_key} record found in database")