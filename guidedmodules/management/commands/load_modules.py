from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from guidedmodules.models import AppSource, AppInstance
from guidedmodules.module_sources import MultiplexedAppStore, AppImportUpdateMode, IncompatibleUpdate

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

                # Update an existing instance of the app if the changes are compatible
                # with the existing data model.
                oldappinst = AppInstance.objects.filter(source=app.store.source, appname=app.name, system_app=True).first()

                # Try to update the existing app.
                try:
                    appinst = app.import_into_database(
                        update_appinst=oldappinst,
                        update_mode=AppImportUpdateMode.CompatibleUpdate if oldappinst else AppImportUpdateMode.CreateInstance)
                except IncompatibleUpdate as e:
                    # App was changed in an incompatible way, so fall back to creating
                    # a new AppInstance and mark the old one as no longer the system_app.
                    # Only one can be the system_app.
                    print(app, e)
                    appinst = app.import_into_database()
                    oldappinst.system_app = None # the correct value here is None, not False, to avoid unique constraint violation
                    oldappinst.save()

                # Mark the new one as a system_app so that organization and account
                # settings can find it.
                if not appinst.system_app:
                    appinst.system_app = True
                    appinst.save()
