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
    help = 'Create a set of dummy data for extended testing/verification'

    def add_arguments(self, parser):
        parser.add_argument('--password')
        
        parser.add_argument('--user-count', type=int, default=20)
        parser.add_argument('--org-count', type=int, default=5)
        parser.add_argument('--print-iter', type=int, default=100)

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
            if ((x+1) % options['print_iter'] == 0):
                print("Created user #" + str(x+1))
        for x in range(0, options['org_count']):
            admin = sample(users, 1)[0]
            help_squad = sample(users, 5)
            reviewers = sample(users, 5)
            org = create_organization(admin=admin, help_squad=help_squad, reviewers=reviewers)
            print("Admin for " + org.name + ": " + admin.username)

            if options['full']:
                protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
                base_url = '{}://{}.{}/'.format(protocol, org.subdomain, settings.ORGANIZATION_PARENT_DOMAIN)
                print("Using base URL: {}".format(base_url))
                print('Adding system...')
                call_command('add_system',  '--password', options['password'], '--username', admin.username, '--base_url', base_url)
                print('Adding assessments...')
                call_command('start_assessment', '--to-completion', '--password', options['password'], '--username', admin.username, '--base_url', base_url)

                print('Prepping assessments (tasks, pass #1)...')
                call_command('answer_all_tasks', '--impute', 'answer', '--org', org.subdomain)

                print('Filling assessments (tasks, pass #2)...')
                call_command('answer_all_tasks', '--impute', 'answer', '--org', org.subdomain)

                final_output.append('Finished org {}. Check {} using user:pass {} : {}'.format(org.name, base_url, admin.username, options['password']))

        for line in final_output:
            print(line)

