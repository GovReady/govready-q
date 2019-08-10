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

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('--non-interactive', action='store_true', help="Don't prompt the user for anything (uses various default values instead)")

    def handle(self, *args, **options): 
        if not options['non_interactive']:
            input("Future versions are expected to ask for user input. For non-interactive usage, run with `--non-interactive`. Waiting for input:\n> ")
            
        call_command('create_and_fill_assessment')
