from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from guidedmodules.models import AppSource
from guidedmodules.module_sources import MultiplexedAppStore, AppImportUpdateMode

class Command(BaseCommand):
    help = 'Updates the system modules from the YAML specifications in AppSources.'

    def add_arguments(self, parser):
        parser.add_argument('force', nargs="?", type=bool)

    def handle(self, *args, **options):
        with MultiplexedAppStore(ms for ms in AppSource.objects.all()) as store:
            for app in store.list_apps():
                # Only load system modules.
                if app.store.source.namespace != "system":
                    continue

                # Import.
                app.import_into_database()
