import sys

from django.core.management.base import BaseCommand
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
  help = 'Check if version 0.9.0 migration has been run.'

  def handle(self, *args, **options):
    migration_exists = MigrationRecorder.Migration.objects.filter(app='siteapp', name='0025_auto_20190515_1455')

    if not migration_exists:
      print("0.9.0 migration has not been run")
      return True
    else:
      print("0.9.0 migration has been run")
      return False
