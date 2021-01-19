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
from loadtesting.data_management import create_user, create_portfolio

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification. Creates users, portfolios, organizations, user/org assignments, and with --full, can also populate the created organizations with assessments.'

    def add_arguments(self, parser):
        parser.add_argument('--password', help="The password to set for all users. Optional, but recommended. If not set, all users will have the same random password, instead.")
        
        parser.add_argument('--user-count', type=int, default=5, help="How many users to create at once")

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
            create_portfolio(u)
            print("Created portfolio for user {}".format(u.username))

        for line in final_output:
            print(line)

