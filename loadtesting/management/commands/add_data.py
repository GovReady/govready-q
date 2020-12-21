import sys
import os.path
import time

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from random import sample
from loadtesting.web import WebClient

import re

# When adding users, we expect they'll be created for test purposes. Therefore, a
# static easy-to-remember pwd is useful.
DEFAULT_USER_PASSWORD="GovReadyTest2019"

class Command(BaseCommand):
    client = None

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('--non-interactive', action='store_true', help="Don't prompt the user for anything (uses various default values instead)")

    def prompt(self, msg):
        return input(msg + "\n> ")
    def prompt_for_time(self, msg):
        msg += "\n   Input format (defaults to seconds):\n   {}".format("12.0 [seconds|minutes|hours]")
        raw = self.prompt(msg)
        pattern = r'^(\d+(?:\.\d+)?)\s*(\w+)?$'
        match = re.match(pattern, raw)
        while not match:
            print("Not a valid time value.")
            raw = self.prompt(msg)
            match = re.match(pattern, raw)

        (num, unit) = match.groups()
        num = float(num)
        if unit:
            unit = unit.lower()

        if not unit or 'seconds'.startswith(unit):
            pass # we've got it in seconds already
        elif 'minutes'.startswith(unit):
            num *= 60
        elif 'hours'.startswith(unit):
            num *= 3600

        return num

    def handle(self, *args, **options):
        delay = 0
        count = 1
        user_count = 0

        if not options['non_interactive']:
            user_count = self.prompt("How many users do you want to create? (0 or more)")
            count = self.prompt("How many assessments do you want to create and populate? (note: if you want to run until canceled, enter a large number, and hit Ctrl-C when you want to stop)")
            print("")
            delay = self.prompt_for_time("It's possible to insert a delay between each action, while generating data. Enter the desired number of seconds to wait, or 0 for no delay.")
            
        start = time.time()

        if int(user_count) > 0:
            call_command("populate", "--user-count", user_count, "--password", DEFAULT_USER_PASSWORD)

        call_command('create_and_fill_assessment', '--action-delay', delay, '--count', count)

        end = time.time()

        # we mostly care about runtime in seconds, so we'll report that
        duration = int(end - start)

        print("Took {} seconds with {} users and {} assessments".format(duration, user_count, count)) 
