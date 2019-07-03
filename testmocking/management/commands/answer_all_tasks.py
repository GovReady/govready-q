import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module, Task
from siteapp.models import User, Organization

from testmocking.data_management import answer_randomly

class Command(BaseCommand):
    help = 'Automatically answers questions in all "Task"s for an org'

    def add_arguments(self, parser):
        parser.add_argument('--org', type=str, required=True, help="the slug for the organization (group) to target")
        parser.add_argument('--impute', choices=['halt', 'skip', 'answer'], default='halt', help="specify 'halt' (the default) to abort on the first non-handled imputed question, 'skip' to ignore it and answer future questions, or 'answer' to answer it despite possibly being imputed")
        parser.add_argument('--quiet', action='store_true', help="Reduces verbosity")

    def handle(self, *args, **options):
        tasks = [task for task in Task.objects.all() if task.project.organization and  task.project.organization.slug == options['org']] 
        for task in tasks:
            print("Handling task {}".format(task.id))

            halt_impute = (options['impute'] == 'halt')
            skip_impute = (options['impute'] == 'skip')
            answer_randomly(task, halt_impute=halt_impute, skip_impute=skip_impute, quiet=options['quiet'])
            print("")
