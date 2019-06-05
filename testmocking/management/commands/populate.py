import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module
from siteapp.models import User, Organization

from testmocking.data_management import create_user

class Command(BaseCommand):
    help = 'Create a set of dummy data for extended testing/verification'

    def handle(self, *args, **options):
        for x in range(0,20):
                create_user();
