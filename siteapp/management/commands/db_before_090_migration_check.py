import sys

from django.core.management.base import BaseCommand
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
  help = 'Check if version 0.9.0 migration has been run.'

  def handle(self, *args, **options):
    site_app_migration_exists = MigrationRecorder.Migration.objects.filter(app='siteapp', name='0025_auto_20190515_1455')
    guardian_migration_exists = MigrationRecorder.Migration.objects.filter(app='guardian', name='0001_initial')
    system_settings_exists = MigrationRecorder.Migration.objects.filter(app='system_settings', name='0002_auto_20190808_1947')

    migration_to_090_occured = False

    if site_app_migration_exists:
      print("site app migrations have been run")
      migration_to_090_occured = True
    if guardian_migration_exists:
      print("guardian migrations have been run")
      migration_to_090_occured = True
    if system_settings_exists:
      print("system_settings migrations have been run")
      migration_to_090_occured = True

    print(migration_to_090_occured)