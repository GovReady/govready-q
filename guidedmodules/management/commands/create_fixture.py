from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

import sys

from siteapp.models import User, Organization, Project, ProjectMembership
from guidedmodules.models import Module, Task

class Command(BaseCommand):
    help = 'Creates a fixture that includes an organization, user, and modules.'

    def add_arguments(self, parser):
        parser.add_argument('projects', nargs="+", type=str)

    def handle(self, *args, **options):
        # Don't actually save to the database the intermediate
        # objects we need to create to make a fixture.
        class RollItBack(Exception): pass
        try:
            with transaction.atomic():
                self.create_fixture(options)
                raise RollItBack()
        except RollItBack:
            # Let the transaction roll back silently.
            pass

    def create_fixture(self, options):
        # Create a user.
        user = User()
        user.username = "test"
        user.set_password("1234")
        user.save()

        # Create an organization.
        org = Organization.create(
            name="Test Organization",
            subdomain="test",
            allowed_modules=options["projects"],
            admin_user=user)

        # All Module and ModuleQuestion instances that are needed.
        # If the Module has questions that depend on other modules,
        # include those in the fixture too, recursively.
        modules = []

        def add_module(m):
            if m in modules: return
            print(m, file=sys.stderr)
            modules.append(m)
            for mq in m.questions.all():
                modules.append(mq)
                if mq.answer_type_module:
                    add_module(mq.answer_type_module)

        required_projects = ["system/account_settings_project", "system/organization/app"]

        for prj_module_key in required_projects + options["projects"]:
            try:
                m = Module.objects.get(key=prj_module_key, visible=True, superseded_by=None)
            except Module.DoesNotExist:
                print("Invalid module ID", prj_module_key, file=sys.stderr)
                return
            add_module(m)

        # Ok, save.
        from django.core import serializers
        print(serializers.serialize("json",
            [user,
            org, org.get_organization_project(), org.get_organization_project().root_task,
            pm] + modules,
            indent=2))

