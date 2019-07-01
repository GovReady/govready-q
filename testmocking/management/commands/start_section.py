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
    bad_comps = []

    help = 'Starts one or many sections for a project'

    def add_arguments(self, parser):
        parser.add_argument('--base_url', type=str, required=True, help="")
        parser.add_argument('--username', type=str, required=True, help="")
        parser.add_argument('--password', type=str, required=True, help="")
        parser.add_argument('--project', type=int, required=True, help="")
        #parser.add_argument('--to-completion', action="store_true", help="")

    def handle(self, *args, **options):
        self.client = WebClient(options['base_url'])
        self.client.login(options['username'], options['password'])


        self.client.start_section_for_proj(options['project'])
        print(self.client.response.url)
