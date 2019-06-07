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

from testmocking.data_management import create_user, create_organization

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification'

    def add_arguments(self, parser):
        parser.add_argument('--password')
        
        parser.add_argument('--user-count', type=int, default=20)
        parser.add_argument('--org-count', type=int, default=5)
        parser.add_argument('--print-iter', type=int, default=100)

    def handle(self, *args, **options):
        users = []
        pw_hash = None
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
            print("Admin: " + admin.username)

