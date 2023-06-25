"""
load_app_template.py
    Create an initial SSP project using the organization's default template.

    Usage:   manage.py load_app_template username path/to/template project_name
    Example: manage.py load_app_template govready laurasia/JSIG_SSP "System Security Plan"
"""

import sys
import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.db.utils import OperationalError
from django.conf import settings

from guidedmodules.models import AppSource, Module, AppVersion
from siteapp.models import User, Organization, Portfolio
from django.contrib.auth.management.commands import createsuperuser
from siteapp.models import User, Project, Organization, Portfolio, Folder
from controls.models import System, Element, ElementControl

import fs, fs.errors


class Command(BaseCommand):
    help = 'Load Initial SSP Project'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?')
        parser.add_argument('template', nargs='?')
        parser.add_argument('project_name', nargs='?')

    def handle(self, *args, **options):
        try:
            # Get user from command line argparse
            user = User.objects.get(username=options['username'])

            # Get user portfolio
            portfolio = Portfolio.objects.get(id=user.default_portfolio_id)

            # Get SSP project name or use default
            project_name = options['project_name']
            if not project_name:
                new_name = "System Security Plan"
                print(f'Using project name default {new_name}')
            else:
                new_name = project_name

            # Verify valid template exists or use default
            template = options['template']
            if not template:
                template = 'laurasia/JSIG_SSP'
            template_exists = ()

            for app in AppVersion.objects.all():
                this_app = str(app.source) + "/" + str(app.appname)
                if this_app == template:
                    template_exists = 1
            if not template_exists:
                print(f'No such template {template}')
                exit()

        except Exception as e:
                print(f'(Exception: {e}')
                exit()

        # Check if project already exists
        project_exists = ()
        for p in Project.objects.all():
            if p.title == new_name:
                project_exists = 1
                existing_project_id = p.id
        if project_exists:
            print(f'Unique contraint violation. Project #{existing_project_id} with name "{new_name}" already exists.')
            # We're done
        else:
            # Our project does not exist, so load default Project
            # Set defaults for testing
            self.org = Organization.objects.first()
            #print(self.org.slug)
            username = user

            from loadtesting.web import WebClient
            client = WebClient(username, "main")

            # Create project
            print("Adding project to portfolio: {} (#{}).".format(portfolio.title, portfolio.id))
            client.post("/store/{}?portfolio={}".format(template, portfolio.id), {"organization":self.org.slug})
            #print(client.response.url)

            # Get newly created project
            project = Project.objects.get(id=client.response.url.split('/')[2])
            print(f'Project created as: {project}')

            # Rename project
            if project:
                # Double check project name does not exist
                project_exists = ()
                for p in Project.objects.all():
                    if p.title == new_name:
                        project_exists = 1
                if not project_exists:
                    project.root_task.title_override = new_name
                    project.root_task.save()
                    project.root_task.on_answer_changed()
                    if project.system is not None:
                        project.system.root_element.name = new_name
                        project.system.root_element.save()
                    print(f"Project renamed to {new_name}.")
                else:
                    print(f'Unique contraint violation. Project with name "{new_name}" already exists. \n\
                            Not renaming "{project.title}"')
