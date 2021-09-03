# Usage:
#   python manage.py makecmmcstatements --component_ids <space-delimted list of element ids> --importname "<name for import record>"
#
# Example:
#   python3 manage.py makecmmcstatements --component_ids 1 6 --importname "Generating CMMC statements"
#
# Example Docker:
#   docker exec -it govready-q-dev python3 manage.py makecmmcstatements --importname "batch import" --component_ids 1 2 4 5 35
#   docker exec -it govready-q-dev python3 manage.py makecmmcstatements --component_ids 1 2 4 5 35 --importname "batch import"

import sys
import os.path

from collections import defaultdict
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings
from pathlib import Path
from pathlib import PurePath
from django.utils.text import slugify

from controls.models import Element, Statement, StatementRemote, ImportRecord
from controls.enums.statements import StatementTypeEnum
from controls.enums.remotes import RemoteTypeEnum
from controls.oscal import *

from controls.views import OSCALComponentSerializer, ComponentImporter

import fs, fs.errors

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory
structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


class Command(BaseCommand):
    help = 'Make CMMC statements from 800-53 statements'

    def add_arguments(self, parser):
        # parser.add_argument('--format', metavar='format', nargs='?', default="oscal", help="File format")
        # parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', default="local/export/components", help="The directory path containing component files to import.")

        parser.add_argument('--importname', metavar='import_name', nargs='?', type=str, default="Batch CMMC component statement creation", help="Name to identify the batch creation of statements")

        parser.add_argument('--component_ids', metavar='component_ids', nargs='+', required=True, type=int, help="Space delimited list of component IDs")

        parser.add_argument('--stopinvalid', default=True, action='store_true')
        parser.add_argument('--no-stopinvalid', dest='stopinvalid', action='store_false')

    def handle(self, *args, **options):

        # Set up
        # Create import record so we easily bulk delete
        import_name = options['importname']
        component_ids = options['component_ids']

        import_rec = ImportRecord.objects.create(name=import_name)
        CIP = StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name

        # Get the CMMC Catalog instance
        catalog_key = "CMMC_ver1"
        cmmc = Catalog.GetInstance(catalog_key=catalog_key)
        c_dict= cmmc.get_flattened_controls_all_as_dict()

        def get_catalog_key_from_ref(ref):
            """Extract the catalog_key from a OSCAL catalog link href string"""
            # Example: get 'NIST_SP-800-171_rev1' from ' "href": "/controls/catalogs/NIST_SP-800-171_rev1/control/3.1.3" '
            # TODO: Make sure GovReady catalogs are consistent in href handling!
            # TODO make parsing mor robust!
            ref_items = ref.split("/")
            catalog_key = ref_items[3]
            return catalog_key

        # Process components and their statements
        emt_smts = Statement.objects.filter(producer_element__in=component_ids, statement_type=CIP).order_by('producer_element')
        smts_grouped = defaultdict(list)
        for s in emt_smts:
            smts_grouped[s.producer_element].append(s)
        for emt in smts_grouped.keys():
            print(f"\n{emt.name} ({emt.id})")
            for smt in smts_grouped[emt]:
                print(f"# Analyze {smt}")
                r = [sid for sid in c_dict.keys() if len([gl['text'] for gl in c_dict[sid]['guidance_links'] if gl['text']==de_oscalize_control_id(smt.sid, get_catalog_key_from_ref(gl['href']) ) ])>0]
                print(f"- Found links to: {r}")
                for rc in r:
                    new_smt, created = Statement.objects.get_or_create(sid=rc, sid_class=catalog_key, producer_element=emt, statement_type=CIP)
                    new_smt.change_log = { "change_log": {"changes": []} }
                    change = {
                        "datetimestamp": new_smt.updated.isoformat(),
                        "event": None,
                        "source": None,
                        "user_id": "admin",
                        "fields": {
                            "sid": new_smt.sid,
                            "sid_class": new_smt.sid_class,
                            "body": new_smt.body
                        }
                    }
                    if created:
                        print(f"- Created smt id {new_smt.id}")
                        new_smt.import_record = import_rec
                        change['event'] = 'created'
                        new_smt.body = smt.body
                        logger.info(event=f"new_statement makecmmcstatements",
                                object={"object": "statement", "id": new_smt.id},
                                user={"id": None, "username": None})
                    else:
                        # TODO test if remote_type origin already exists for record and skip if exists
                        print(f"- Updating smt id {new_smt.id}")
                        if new_smt.body is None: new_smt.body = ""
                        new_smt.body = new_smt.body + "\n\n" + smt.body
                        change['event'] = 'updated'
                        logger.info(event=f"update_statement makecmmcstatements",
                                object={"object": "statement", "id": new_smt.id},
                                user={"id": None, "username": None})
                    change['fields']['body'] = new_smt.body
                    new_smt.change_log_add_entry(change)
                    new_smt.save()
                    # Create remote record
                    smt_r = StatementRemote.objects.create(statement=new_smt, remote_statement=smt, remote_type=RemoteTypeEnum.ORIGIN.name)

