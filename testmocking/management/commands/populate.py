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

    def handle(self, *args, **options):
        users = []
        for x in range(0, options['user_count']):
            u = create_user(password=options['password'])
            users += [u]
        for x in range(0, options['org_count']):
            admin = sample(users, 1)[0]
            org = create_organization(admin=admin)
            print("Admin: " + admin.username)

