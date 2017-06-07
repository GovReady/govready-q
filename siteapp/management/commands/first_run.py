from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.conf import settings

from siteapp.models import User, Organization
from django.contrib.auth.management.commands import createsuperuser

class Command(BaseCommand):
    help = 'Interactively set up an initial user and organization.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Create the first user.
        if not User.objects.filter(is_superuser=True).exists():
            print("Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.")
            call_command('createsuperuser')

        # Create the first organization.
        if not Organization.objects.exists():
            print("Let's create your Q organization.")
            name = Organization._meta.get_field("name")
            get_input = createsuperuser.Command().get_input_data
            
            name = get_input(name, "Organization Name: ", "Test Organization")
            
            org = Organization.create(name=name, subdomain="main", admin_user=User.objects.filter(is_superuser=True).first())
