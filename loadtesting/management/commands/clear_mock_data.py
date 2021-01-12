import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization

from loadtesting.data_management import delete_objects

class Command(BaseCommand):
    help = 'Clear all data created for mock purposes'

    def handle(self, *args, **options):
        delete_objects(Organization)
        delete_objects(User)
