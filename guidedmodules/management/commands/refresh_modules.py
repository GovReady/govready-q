from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from guidedmodules.models import ModuleSource
from guidedmodules.module_sources import MultiplexedAppStore, AppImportUpdateMode

class Command(BaseCommand):
    help = 'For debugging, updates Tasks to the latest versions of Apps.'

    def add_arguments(self, parser):
        parser.add_argument('force', nargs="?", type=bool)

    def handle(self, *args, **options):
        with MultiplexedAppStore(ms for ms in ModuleSource.objects.all()) as store:
            for app in store.list_apps():
                try:
                    app.import_into_database(
                        AppImportUpdateMode.ForceUpdateInPlace
                         if options.get("force") == True
                         else AppImportUpdateMode.UpdateIfCompatibleOnly)
                except Exception as e:
                    # If there's an error with this app, just print it and
                    # continue to try to refresh other apps.
                    print("Unhandled error loading", app, e)

