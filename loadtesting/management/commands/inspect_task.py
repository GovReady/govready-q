import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module, Task, TaskAnswer
from siteapp.models import User, Organization

from loadtesting.data_management import answer_randomly

class Command(BaseCommand):
    help = 'Shows some development information on a Task, by ID'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, required=True)
        parser.add_argument('--spacer', action="store_true", help="Add a blank line after certain portions of the output")

    def handle(self, *args, **options):
        task = Task.objects.filter(id=options['id'])[0]

        for question in task.module.questions.order_by('definition_order'):
            print(self.format_question(question))
            if question.spec['type'] == 'module':
                print("{}".format(question.spec))
                print("")
            
            taskans = TaskAnswer.objects.filter(task=task, question=question).first()
            if taskans:
                print(taskans.get_current_answer().stored_value)
                if options['spacer']:
                    print("")

    def format_question(self, question):
        key = question.key
        mod_id = question.module.id
        id = question.id
        type = question.spec['type']
        return "[q #{}] module_{} . {}, type '{}'".format(id, mod_id, key, type)
