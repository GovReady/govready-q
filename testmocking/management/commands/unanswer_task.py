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
    help = 'Removes one layer of answers from a Task'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, required=True, help="the ID of the task you want to unanswer")

    def handle(self, *args, **options):
        task = Task.objects.filter(id=options['id'])[0]

        answer_history = [pair[1] for pair in task.get_current_answer_records() if pair[1]]
        for entry in answer_history:
            entry.delete()
        print("Deleted {} answers".format(len(answer_history)))
