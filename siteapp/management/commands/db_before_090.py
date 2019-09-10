import sys

from django.core.management.base import BaseCommand
from django.db.migrations.recorder import MigrationRecorder
from django.db import DatabaseError


class Command(BaseCommand):
  """Protect Admins from accidentally migrating their database to 0.9.0 before they have prepared."""
  help = 'Check if version 0.9.0 migration has been run. Return "False" if database not initialized or 0.9.0 migrations has been run.'

  def handle(self, *args, **options):
    site_app_migration_exists = MigrationRecorder.Migration.objects.filter(app='siteapp', name='0025_auto_20190515_1455')
    guardian_migration_exists = MigrationRecorder.Migration.objects.filter(app='guardian', name='0001_initial')
    system_settings_exists = MigrationRecorder.Migration.objects.filter(app='system_settings', name='0002_auto_20190808_1947')

    # Assume case of existing Database initialized and in state prior to 0.9.0
    DB_BEFORE_090 = "True"

    try:
      if site_app_migration_exists:
        DB_BEFORE_090 = "False"
      if guardian_migration_exists:
        DB_BEFORE_090 = "False"
      if system_settings_exists:
        DB_BEFORE_090 = "False"
    except DatabaseError:
        # Treat case of database not initialized as OK to run 0.9.0 migrations
        DB_BEFORE_090 = "False"

    print(DB_BEFORE_090)
