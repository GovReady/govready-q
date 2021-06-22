from django.core.management.base import BaseCommand

from controls.enums.statements import StatementTypeEnum
from controls.models import Statement, ImportRecord
from siteapp.models import User, Project, Organization
import xlsxio


class Command(BaseCommand):
    help = 'Import CSAM System Implementation Statement Query excel export'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?')

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
                    record = dict(control_number=row[5], implementation_statement=row[7])
                    if system_name not in process_data:
                        process_data[system_name] = []
                    process_data[system_name].append(record)

        org = Organization.objects.first()
        user = User.objects.all()[1]  # hardcode to second user (first user that was created)

        for system_name, data in process_data.items():
            project = Project.objects.filter(system__root_element__name=system_name).first()
            if not project:
                from loadtesting.web import WebClient
                client = WebClient(user.username, "main")
                client.post("/store/govready-q-files-startpack/blank",
                            {"organization": org.slug})
                project = Project.objects.get(id=client.response.url.split('/')[2])

                project.root_task.title_override = system_name
                project.root_task.save()
                project.root_task.on_answer_changed()
                if project.system is not None:
                    project.system.root_element.name = system_name
                    project.system.root_element.save()
            existing_statements = Statement.objects.filter(sid__in=[row['control_number'] for row in data],
                                                           sid_class="NIST_SP-800-53_rev4",
                                                           producer_element=project.system.root_element,
                                                           consumer_element=project.system.root_element)
            existing_statement_sids = existing_statements.values_list('sid', flat=True)
            create_statements = []
            import_record = ImportRecord.objects.create(name=options['file'])
            for row in data:
                if row['control_number'] in existing_statement_sids:
                    # Update if exists
                    record = self.find(row['control_number'], 'sid', existing_statements)
                    if record.body != row['implementation_statement']:
                        record.body = row['implementation_statement']
                        record.import_record = import_record
                        record.save()
                else:
                    # Create if doesn't exist
                    create_statements.append(Statement(sid=row['control_number'],
                                                       sid_class="NIST_SP-800-53_rev4",
                                                       producer_element=project.system.root_element,
                                                       consumer_element=project.system.root_element,
                                                       body=row['implementation_statement'],
                                                       statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_LEGACY,
                                                       remarks='imported from spreadsheet',
                                                       import_record=import_record))

            if create_statements:
                # Bulk insert the creates
                Statement.objects.bulk_create(create_statements)

            if not import_record.import_record_statements.exists():
                # Removes the import record object IF there were no creates or updates.
                import_record.delete()
