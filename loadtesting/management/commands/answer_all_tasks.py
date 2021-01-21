import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module, Task
from siteapp.models import User, Organization

from loadtesting.data_management import answer_randomly

from time import sleep, ctime

class Command(BaseCommand):
    help = 'Automatically answers questions in all "Task"s for an org'

    def add_arguments(self, parser):
        parser.add_argument('--org', type=str, required=True, help="the slug for the organization (group) to target")
        parser.add_argument('--impute', choices=['halt', 'skip', 'answer'], default='halt', help="specify 'halt' (the default) to abort on the first non-handled imputed question, 'skip' to ignore it and answer future questions, or 'answer' to answer it despite possibly being imputed")
        parser.add_argument('--quiet', action='store_true', help="Reduces verbosity")
        parser.add_argument('--delay', default=0, type=float, help="Number of seconds to wait between each action. Must be non-negative (0 is no delay)")
        parser.add_argument('--task_ids', type=str, help="comma-separated list of ints. if provided, filter to only these tasks (`id` field in DB)")

    def handle(self, *args, **options):

        def delay():
            if options['delay'] > 0:
                print("pausing for {} seconds -- at {}".format(options['delay'], ctime()))
                sleep(options['delay'])

        query = Task.objects.all()
        if options['task_ids']:
            query = Task.objects.filter(id__in=options['task_ids'].split(','))

        tasks = [task for task in query if task.project.organization and  task.project.organization.slug == options['org']] 

        # sooo... sometimes we might have accidentally created a project with no admin. Use the org admin instead.
        dummy_user = tasks[0].project.organization.get_organization_project().get_admins()[0]

        for task in tasks:
            print("Handling task {}".format(task.id))

            halt_impute = (options['impute'] == 'halt')
            skip_impute = (options['impute'] == 'skip')
            did_anything = answer_randomly(task, dummy_user, halt_impute=halt_impute, skip_impute=skip_impute, quiet=options['quiet'])
            if did_anything:
                delay()
            else:
                print("Fully skipped")

            print("")
