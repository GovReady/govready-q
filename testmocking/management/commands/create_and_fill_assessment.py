import sys
import os.path
from random import sample


from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization

from django.utils.crypto import get_random_string
from time import sleep, ctime

import subprocess

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification'

    def add_arguments(self, parser):
        parser.add_argument('--count', default=1, type=int, help="Number of iterations to run (i.e., how many systems to add)")
        parser.add_argument('--action-delay', default=0, type=float, help="Number of seconds to wait between each action. Must be non-negative (0 is no delay)")

    def handle(self, *args, **options):
        def echo_section(info):
            print("=== {} ===".format(info))

        admin = User.objects.get(id=2)
        org_slug = 'main'

        def delay():
            if options['action_delay'] > 0:
                print("pausing for {} seconds -- at {}".format(options['action_delay'], ctime()))
                sleep(options['action_delay'])

        for x in range(0, options['count']):
            echo_section('Adding system...')
            call_command('add_system', '--username', admin.username, '--org', org_slug)
            delay()
            echo_section('Adding assessments...')
            call_command('start_section', '--to-completion', '--username', admin.username, '--org', org_slug, '--delay', options['action_delay'])
            delay()

            echo_section('Prepping assessments (tasks, pass #1)...')
            call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug, '--delay', options['action_delay'])
            delay()

            echo_section('Filling assessments (tasks, pass #2)...')
            call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug, '--delay', options['action_delay'])
