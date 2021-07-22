from django.core.management.base import BaseCommand

from controls.enums.statements import StatementTypeEnum
from controls.models import Statement, ImportRecord
from controls.utilities import oscalize_control_id
from siteapp.models import User, Project, Organization
import xlsxio
import os

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

# Example:
# python3 manage.py import_csam_statements SystemImplementationStatementsQuery.xlsx admin

class Command(BaseCommand):
    help = 'Import CSAM System Implementation Statement Query excel export'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?')
        parser.add_argument('username', nargs='?')

    def find(self, target, prop, array):
        for i in range(len(array)):
            if getattr(array[i], prop) == target:
                return array[i]

    def handle(self, *args, **options):
        process_data = {}
        with xlsxio.XlsxioReader(options['file']) as reader:
            with reader.get_sheet() as sheet:
                sheet.read_header()  # Skip first row since it contains the classification banner
                header = sheet.read_header()
                rows = sheet.read_data()
                for row in rows:
                    system_name = row[3]
                    record = dict(control_number=row[5], implementation_statement=row[9])
                    if system_name not in process_data:
                        process_data[system_name] = []
                    process_data[system_name].append(record)

        org = Organization.objects.first()
        user = User.objects.get(username=options['username'])

        import_record = ImportRecord.objects.create(name=os.path.basename(options['file']))

        for system_name, data in process_data.items():
            project = Project.objects.filter(system__root_element__name=system_name).first()
            if not project:
                from loadtesting.web import WebClient
                client = WebClient(user.username, "main")
                client.post("/store/govready-q-files-startpack/blank",
                            {"organization": org.slug})
                project = Project.objects.get(id=client.response.url.split('/')[2])
                project.import_record = import_record
                project.save()

                project.root_task.title_override = system_name
                project.root_task.save()
                project.root_task.on_answer_changed()
                if project.system is not None:
                    project.system.root_element.name = system_name
                    project.system.root_element.import_record = import_record
                    project.system.root_element.save()
                # Set baseline if not set
                # baseline_name = [p for p in parameters if p['id'] == 'baseline'][0]['value']
                # Assign profile/baseline
                catalog_key="NIST_SP-800-53_rev4"
                baseline_name = "moderate"
                assign_results = project.system.root_element.assign_baseline_controls(user, catalog_key, baseline_name)
                # Log result if successful
                if assign_results:
                    # Log start app / new project
                    logger.info(
                        event="assign_baseline",
                        object={"object": "system", "id": project.system.root_element.id, "title": project.system.root_element.name},
                        baseline={"catalog_key": catalog_key, "baseline_name": baseline_name},
                        user={"id": user.id, "username": user.username}
                    )

            existing_statements = Statement.objects.filter(sid__in=[oscalize_control_id(row['control_number']) for row in data],
                                                           sid_class="NIST_SP-800-53_rev4",
                                                           producer_element=project.system.root_element,
                                                           consumer_element=project.system.root_element)
            existing_statement_sids = existing_statements.values_list('sid', flat=True)
            create_statements = []
            for row in data:
                oscal_control_id = oscalize_control_id(row['control_number'])
                if oscal_control_id in existing_statement_sids and row['implementation_statement']:
                    # Update smt if exists
                    record = self.find(oscal_control_id, 'sid', existing_statements)
                    if record.body != row['implementation_statement']:
                        record.body = row['implementation_statement']
                        record.import_record = import_record
                        record.save()
                elif oscal_control_id in existing_statement_sids and not row['implementation_statement']:
                    # Delete smt if exists and incoming implementation_statement is empty
                    record = self.find(oscal_control_id, 'sid', existing_statements)
                    record.delete()
                elif row['implementation_statement']:
                    # Create smt if doesn't exist
                    create_statements.append(Statement(sid=oscal_control_id,
                                                       sid_class="NIST_SP-800-53_rev4",
                                                       producer_element=project.system.root_element,
                                                       consumer_element=project.system.root_element,
                                                       body=row['implementation_statement'],
                                                       statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_LEGACY.name,
                                                       remarks='imported from spreadsheet',
                                                       import_record=import_record))

            if create_statements:
                # Bulk insert the creates
                Statement.objects.bulk_create(create_statements)

            if not import_record.import_record_statements.exists():
                # Removes the import record object IF there were no creates or updates.
                try:
                    import_record.delete()
                except:
                    pass

