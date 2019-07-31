import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from random import sample
from testmocking.web import WebClient

from guidedmodules.models import Project

class Command(BaseCommand):
    client = None
    bad_comps = []

    help = 'Starts one or many sections for a project'

    def add_arguments(self, parser):
        parser.add_argument('--org', default='main' type=str, required=True, help="slug of the org to use (largely ignored, defaults to 'main')")
        parser.add_argument('--username', type=str, required=True, help="username to act on behalf of")
        parser.add_argument('--project', type=int, required=False, help="the project ID to target. If omitted, the most-recent project will be used instead")
        parser.add_argument('--to-completion', action="store_true", help="")

    def handle(self, *args, **options):
        self.client = WebClient(options['username'], options['org'])

        project = options['project']
        if not project:
            project = Project.objects.all().order_by('id').last().id
            print("No project ID specified, using most recent ID ({}) instead".format(project))

        count = self.client.start_section_for_proj(project)
        print("{} sections available at the start".format(count))
        if options['to_completion']:
            while count > 1:
                count = self.client.start_section_for_proj(project)
