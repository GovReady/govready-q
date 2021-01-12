import sys
import os.path
from random import sample
import time


from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module, Task
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
            initial_task_count = Task.objects.count()

            echo_section('Adding system...')
            sys_t0 = time.time()
            call_command('add_system', '--username', admin.username, '--org', org_slug)
            delay()
            sys_t1 = time.time()

            echo_section('Adding assessments...')
            assess_t0 = time.time()
            call_command('start_section', '--to-completion', '--username', admin.username, '--org', org_slug, '--delay', options['action_delay'])
            delay()
            assess_t1 = time.time()
            echo_section('Adding assessments...')

            current_task_count = Task.objects.count()

            # only do the newly-added tasks. (should probably rejigger this so it doesn't rely on checking count)
            task_ids = ','.join([str(x) for x in range(initial_task_count, current_task_count)])

            ans_t0 = time.time()
            echo_section('Prepping assessments (tasks, pass #1)...')
            call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug, '--delay', options['action_delay'], '--task_ids', task_ids)
            delay()

            echo_section('Filling assessments (tasks, pass #2)...')
            call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org_slug, '--delay', options['action_delay'], '--task_ids', task_ids)
            ans_t1 = time.time()
            # with open('benchmark.tmp', 'a') as file:
            #     file.write("add_system: {} sec\n".format(sys_t1 - sys_t0))
            #     file.write("start_section: {} sec\n".format(assess_t1 - assess_t0))
            #     file.write("answer_all_tasks: {} sec\n".format(ans_t1 - ans_t0))
            #     file.write("\n")
