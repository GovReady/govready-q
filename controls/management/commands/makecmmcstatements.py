import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings
from pathlib import Path
# Usage
#   docker exec -it govready_q_dev python3 manage.py makecmmcstatements --importname "batch import" --component_ids 1 2 4 5 35
#   docker exec -it govready_q_dev python3 manage.py makecmmcstatements --component_ids 1 2 4 5 35 --importname "batch import"
from pathlib import PurePath
from django.utils.text import slugify

# from siteapp.models import User, Organization, Portfolio
from controls.models import Element, Statement, StatementRemote, ImportRecord
from controls.enums.statements import StatementTypeEnum
from controls.enums.remotes import RemoteTypeEnum
from controls.oscal import *

# from controls.views import system_element_download_oscal_json
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
        # print(f"existing ids", [e.id for e in Element.objects.all()])
        # sys.exit()

        # Get the CMMC Catalog instance
        catalog_key = "CMMC_ver1"
        cmmc = Catalog.GetInstance(catalog_key=catalog_key)
        c_dict= cmmc.get_flattened_controls_all_as_dict()

        # Start with a list of components from ids
        emts = Element.objects.in_bulk(component_ids)

        for emt_id in emts:
            emt = emts[emt_id]
            emt_smts = emt.statements(CIP)
            for smt in emt_smts:
                print(f"\nTrying {emts[emt_id].name} smt {smt}")
                r = [sid for sid in c_dict.keys() if len([gl['text'] for gl in c_dict[sid]['guidance_links'] if gl['text']==de_oscalize_control_id(smt.sid) ])>0]
                print("r",r)
                for rc in r:
                    new_smt, created = Statement.objects.get_or_create(sid=rc, sid_class=catalog_key, producer_element=emt, statement_type=CIP)
                    print("smt, created", smt, created)
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
                        new_smt.import_record = import_rec
                        change['event'] = 'created'
                        new_smt.body = smt.body
                        logger.info(event=f"new_statement makecmmcstatements",
                                object={"object": "statement", "id": new_smt.id},
                                user={"id": None, "username": None})
                    else:
                        # TODO test if remote_type origin already exists for record and skip if exists
                        new_smt.body = new_smt.body or "" + "\n\n" + smt.body
                        change['event'] = 'updated'
                        logger.info(event=f"update_statement makecmmcstatements",
                                object={"object": "statement", "id": new_smt.id},
                                user={"id": None, "username": None})
                    change['fields']['body'] = new_smt.body
                    new_smt.change_log_add_entry(change)
                    new_smt.save()
                    smt_r = StatementRemote.objects.create(statement=new_smt, remote_statement=smt, remote_type=RemoteTypeEnum.ORIGIN.name)

