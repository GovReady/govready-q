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
        parser.add_argument('--org', type=str, required=True, help="")
        parser.add_argument('--username', type=str, required=True, help="")
        parser.add_argument('--password', type=str, required=True, help="")

    def handle(self, *args, **options):
        self.client = WebClient(options['username'], options['org'])

        self.client.add_system()
