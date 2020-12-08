import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from random import sample
from loadtesting.web import WebClient

from guidedmodules.models import Project

from time import sleep, ctime

class Command(BaseCommand):
    client = None
    bad_comps = []

    help = 'Starts one or many sections for a project'

    def add_arguments(self, parser):
        parser.add_argument('--org', default='main', type=str, required=True, help="slug of the org to use (largely ignored, defaults to 'main')")
        parser.add_argument('--username', type=str, required=True, help="username to act on behalf of")
        parser.add_argument('--project', type=int, required=False, help="the project ID to target. If omitted, the most-recent project will be used instead")
        parser.add_argument('--to-completion', action="store_true", help="")
        parser.add_argument('--delay', default=0, type=float, help="Number of seconds to wait between each action. Must be non-negative (0 is no delay)")

    def handle(self, *args, **options):
        def delay():
            if options['delay'] > 0:
                print("pausing for {} seconds -- at {}".format(options['delay'], ctime()))
                sleep(options['delay'])

        self.client = WebClient(options['username'], options['org'])

        project = options['project']
        if not project:
            project = Project.objects.all().order_by('id').last().id
            print("No project ID specified, using most recent ID ({}) instead".format(project))

        count = self.client.start_section_for_proj(project)
        print("{} sections available at the start".format(count))
        if options['to_completion']:
            while count > 1:
                delay()
                count = self.client.start_section_for_proj(project)
