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
from controls.views import OSCALComponentSerializer

import fs, fs.errors


class Command(BaseCommand):
    help = 'Export all components.'

    def add_arguments(self, parser):
        parser.add_argument('--format', metavar='format', nargs='?', default="oscal", help="File format")
        parser.add_argument('--path', metavar='dir_or_pdf', nargs='?', default="local/export/components", help="The directory path to write export file(s) into.")

    def handle(self, *args, **options):

        # Configure
        FORMAT = options['format']
        EXPORT_PATH = options['path']
        # Create export directory path
        if not os.path.exists(EXPORT_PATH):
            Path(EXPORT_PATH).mkdir(parents=True, exist_ok=True)

        # Export the component library
        elements = Element.objects.filter(element_type="system_element")
        element_cnt = len(elements)

        if FORMAT == 'oscal':
            counter = 0
            for element in elements:
                counter += 1
                print(f"{counter} id: {element.id}, element: {element.name}")
                # Get the impl_smts for component
                impl_smts = Statement.objects.filter(producer_element=element)
                filename = str(PurePath(slugify(element.name)).with_suffix('.json'))
                body = OSCALComponentSerializer(element, impl_smts).as_json()
                # Save component OSCAL
                with open(os.path.join(EXPORT_PATH,filename), "w") as f:
                    f.write(body)
        elif FORMAT == "csv":
            import csv
            counter = 0
            for element in elements:
                counter += 1
                print(f"{counter} id: {element.id}, element: {element.name}")
                # Get the impl_smts for component
                impl_smts = Statement.objects.filter(producer_element=element)
                filename = str(PurePath(slugify(element.name)).with_suffix('.csv'))
                tags = ";".join([f"'{tag.label}'" for tag in element.tags.all()])
                with open(os.path.join(EXPORT_PATH,filename), mode='w') as f:
                    component_writer = csv.writer(f, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    component_writer.writerow(["component_name",
                                               "component_uuid",
                                               "component_tags",
                                               "control_key",
                                               "control_id",
                                               "control_part",
                                               "statement_uuid",
                                               "statement",
                                               "statement_type",
                                               "remarks",
                                               "version",
                                               "created",
                                               "updated"
                                              ])
                    for smt in impl_smts:
                        component_writer.writerow([element.name,
                                                   element.uuid,
                                                   tags,
                                                   smt.sid_class,
                                                   smt.sid,
                                                   smt.pid,
                                                   smt.uuid,
                                                   smt.body,
                                                   smt.statement_type,
                                                   smt.remarks,
                                                   smt.version,
                                                   smt.created,
                                                   smt.updated
                                                  ])
        else:
            counter = 0
            print(f"Format '{FORMAT}' not yet supported.")

        # Done
        print(f"Exported {counter} components in {FORMAT} to folder `{EXPORT_PATH}`.")

