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

import subprocess

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        def echo_section(info):
            print("=== {} ===".format(info))

        admin = User.objects.get(id=1)
        org_slug = 'main'

        echo_section('Adding system...')
        call_command('add_system', '--username', admin.username, '--org', org_slug)
        echo_section('Adding assessments...')
        call_command('start_section', '--to-completion', '--username', admin.username, '--org', org_slug)

        echo_section('Prepping assessments (tasks, pass #1)...')
        call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug)

        echo_section('Filling assessments (tasks, pass #2)...')
        call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug)
