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
from testmocking.data_management import create_user, create_organization

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification. Creates users, organizations, user/org assignments, and with --full, can also populate the created organizations with assessments.'

    def add_arguments(self, parser):
        parser.add_argument('--password', help="The password to set for all users. Optional, but recommended. If not set, all users will have the same random password, instead.")
        
        parser.add_argument('--user-count', type=int, default=5, help="How many users to create at once")
        parser.add_argument('--org-count', type=int, default=1, help="How many organizations to create at once")

        parser.add_argument('--full', action="store_true", help="Also start and fill out assessments, etc., for each organization")

    def handle(self, *args, **options):
        users = []
        pw_hash = None
        final_output = []
        if options['password'] == None:
            options['password'] = get_random_string(16)
        for x in range(0, options['user_count']):
            u = create_user(password=options['password'], pw_hash=pw_hash)
            pw_hash = u.password # MASSIVE performance optimization here
            users += [u]
            if ((x+1) % 100 == 0):
                print("Created user #" + str(x+1))
        for x in range(0, options['org_count']):
            admin = sample(users, 1)[0]
            help_squad = sample(users, 5)
            reviewers = sample(users, 5)
            org = create_organization(admin=admin, help_squad=help_squad, reviewers=reviewers)
            print("Admin for " + org.name + ": " + admin.username)

            if options['full']:
                print('Adding system...')
                call_command('add_system', '--username', admin.username, '--org', org.slug)
                print('Adding assessments...')
                call_command('start_section', '--to-completion', '--username', admin.username, '--org', org.slug)

                print('Prepping assessments (tasks, pass #1)...')
                call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org.slug)

                print('Filling assessments (tasks, pass #2)...')
                call_command('answer_all_tasks', '--quiet', '--impute', 'answer', '--org', org.slug)

                final_output.append('Finished org {}. Login using user:pass {} : {}'.format(org.name, admin.username, options['password']))

        for line in final_output:
            print(line)

