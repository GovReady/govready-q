"""
load_a component from library

Move to controls/management/commands
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
from controls.models import System, Element, ElementControl, Statement

#schaadm additions
from django.contrib import messages
from controls.enums.statements import StatementTypeEnum
from django.db import transaction


class Command(BaseCommand):
    help = 'Load Library Components into SSP'

    def add_arguments(self, parser):
        parser.add_argument('--username', nargs='?')
        parser.add_argument('--component', nargs='?')
        parser.add_argument('--project_name', nargs='?')
        parser.add_argument('--debug', nargs='?')

    @transaction.atomic
    def handle(self, *args, **options):
        debug = False
        try:
            # Get user from command line argparse
            user = User.objects.get(username=options['username'])
            component = options['component']
            project_name = options['project_name']
            if (options['debug']):
                debug = eval(options['debug'])
            print(f'Request parameters username: {user}, component: {component}, project_name: {project_name}, debug: {debug}') if debug else False
        except Exception as e:
            print(f'Exception missing parameter: {e}')
            exit()

        """Add an existing element and its statements to a system"""
        
         # extract producer_elment.id and require_approval boolean val
        try:
            producer_element = Element.objects.filter(name=component).first() # or [0]
            if producer_element == None:
                raise Exception(component)
        except Exception as e:
            print(f'Exception: component not found: {e}')
            exit()

        # Does requested project match an existing project name?
        try:
            project = Project.objects.filter(system__root_element__name=project_name).first()
            system = project.system
            #system = System.objects.get(pk=system_id)
        except Exception as e:
            print(f'Exception finding project name: {e}')
            exit()

        # Does user have permission to add element?
        # Check user permissions
        try:
            project_member = False
            members = User.objects.filter(projectmembership__project=project)
            for member in members:
                print(f'Comparing project membership for {member.username}:{user}') if debug else False
                if member.username == user.username:
                    project_member  = member.username
            if not project_member:
                raise Exception(user.username)
        except Exception as e:
            print(f"Forbidden: user is not a member of project. {e}")
            exit()

        # DEBUG
        print(f"Atempting to add {producer_element.name} (id:{producer_element.id}) to system_id {system.id}") if debug else False

        # Get system's existing components selected
        elements_selected = system.producer_elements
        elements_selected_ids = [e.id for e in elements_selected]

        # Add element to system's selected components
        # Look up the element rto add
        # producer_element = Element.objects.get(pk=producer_element_id)

        # Component already added to system. Do not add the component (element) to the system again.
        if producer_element.id in elements_selected_ids:
            print(f'Component "{producer_element.name}" already exists in selected components.')
            exit()
                
        smts = Statement.objects.filter(producer_element_id = producer_element.id, statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name)

        # Component does not have any statements of type control_implementation_prototype to
        # add to system. So we cannot add the component (element) to the system.
        if len(smts) == 0:
            print(f"Add component error: {producer_element.name} does not have any control implementation statements.")
            exit()

        # Loop through all element's prototype statements and add to control implementation statements.
        # System's selected controls will filter what controls and control statements to display.
        for smt in smts:
            smt.create_system_control_smt_from_component_prototype_smt(system.root_element.id)

        # Make sure some controls were added to the system. Report error otherwise.
        smts_added = Statement.objects.filter(producer_element_id = producer_element.id, consumer_element_id = system.root_element.id, statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name)

        smts_added_count = len(smts_added)
        if smts_added_count > 0:
            print(f'Added "{producer_element.name}" and its {smts_added_count} control implementation statements to the system.')
        else:
            print(f'Error: 0 controls added for component "{producer_element.name}".')
    