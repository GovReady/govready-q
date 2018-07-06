from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from guidedmodules.models import AppSource
from guidedmodules.app_source_connections import MultiplexedAppSourceConnection

class Command(BaseCommand):
    help = 'Prints a list of all apps in the configured app stores.'

    def handle(self, *args, **options):
        with MultiplexedAppSourceConnection(ms for ms in AppSource.objects.all()) as store:
            for app in store.list_apps():
                print(app.store.source.slug, app.name)



