import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from random import sample
from testmocking.web import WebClient

class Command(BaseCommand):
    client = None

    help = 'Adds a System to an organization'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help="")
        parser.add_argument('--password', type=str, required=True, help="")

    def handle(self, *args, **options):
        self.client = WebClient(settings.SITE_ROOT_URL)
        self.client.load('')
        self.client.login(options['username'], options['password'])

        self.client.add_system()
