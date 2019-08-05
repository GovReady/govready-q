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

    def prompt(self, msg):
        return input(msg + "\n> ")

    def handle(self, *args, **options):
        delay = 0
        count = 1

        if not options['non_interactive']:
            count = self.prompt("How many assessments do you want to create and populate? (note: if you want to run until canceled, enter a large number, and hit Ctrl-C when you want to stop)")
            delay = self.prompt("It's possible to insert a delay between each action, while generating data. Enter the desired number of seconds to wait, or 0 for no delay.")
            
        call_command('create_and_fill_assessment', '--action-delay', delay, '--count', count)
