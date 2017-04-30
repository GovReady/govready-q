from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from guidedmodules.models import ModuleSource
from guidedmodules.module_sources import MultiplexedAppStore, AppImportUpdateMode

class Command(BaseCommand):
    help = 'Updates the system modules from the YAML specifications in ModuleSources.'

    def add_arguments(self, parser):
        parser.add_argument('force', nargs="?", type=bool)

    def handle(self, *args, **options):
        with MultiplexedAppStore(ms for ms in ModuleSource.objects.all()) as store:
            for app in store.list_apps():
                app.import_into_database(
                    AppImportUpdateMode.ForceUpdateInPlace
                     if options.get("force") == True
                     else AppImportUpdateMode.UpdateIfCompatible)

