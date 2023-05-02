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
        debug = True
        try:
            # Get catalog/baseline from command line argparse
            catalog_key   = options['catalog_key']
            catalog_json  = options['catalog_file']
            baselines_json = options['baseline']
            if (options['debug']):
                debug = eval(options['debug'])
            print(f'Request parameters catalog_key: {catalog_key}, catalog_file: catalog_json, '
                  f'baseline: baselines_json, debug: {debug}') if debug else False
            if catalog_key == None:
                raise Exception('No catalog_key specified')
            if catalog_json == None:
                raise Exception('No catalog_file specified')
            if baselines_json == None:
                raise Exception('No baseline specified')
        except Exception as e:
                print(f'Exception: {e}')
                exit()

        try:
            for cf in (catalog_json, baselines_json):
                # It's json, but is it really a catalog?
                is_json = json.dumps(cf)
                if not is_json:
                    raise Exception(f'{is_json}')
        except Exception as e:
                print(f'Parsing Exception: {e}')
                exit()

        try:
            catalog, created = CatalogData.objects.get_or_create(
                catalog_key     = catalog_key,
                catalog_json    = catalog_json,
                baselines_json  = baselines_json
            )
            if created:
                print(f"{catalog_key} record created into database")
                print(f"CATALOG created: {catalog} ")
            else:
                print(f"{catalog_key} record found in database")
        except Exception as e:
                print(f'Catalog Exception: {e}')
                exit()
