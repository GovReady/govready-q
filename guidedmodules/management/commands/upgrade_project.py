from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

from siteapp.models import Project
from guidedmodules.models import AppSource, AppVersion, Module, ModuleQuestion, Task, TaskAnswer
from guidedmodules.app_loading import is_module_changed

class Command(BaseCommand):
    help = 'Upgrades a project to a new version of an app or associates a project with a different compliance app.'

    def add_arguments(self, parser):
        parser.add_argument('project', type=int, help="The ID of a siteapp.Project instance to upgrade.")
        parser.add_argument('app_source', nargs="?", type=str, help="The name (slug) of an AppSource containing the AppVersion to upgrade to.")
        parser.add_argument('app_name', nargs="?", type=str, help="The name of an AppVersion within the named AppSource.")
        parser.add_argument('app_version', nargs="?", type=str, help="The version number of the AppVersion to upgrade to.")

    def handle(self, *args, **options):
        project = Project.objects.get(id=options["project"])
        if not options["app_version"]:
            # If run without a source, app name, or version, then we list
            # the available versions of the app.
            self.show_available_versions_to_upgrade_to(project, options)
        else:
            # If a source, app name, and version are specified, then we
            # upgrade the project to that app.
            self.upgrade_app(project, options)

    def show_available_versions_to_upgrade_to(self, project, options):
        # Show all available app source, name, and version tuples that
        # can be upgraded to. Get the app source and app name --- if
        # it's specified on the command line use them, otherwise fall
        # back to the project's current app's info.
        app_source = AppSource.objects.filter(slug=options["app_source"]).first() \
                     or project.root_task.module.source
        app_name = options["app_name"] or project.root_task.module.app.appname

        # Get the AppVersion instances that match the filters.
        app_versions = AppVersion.objects.filter(
            source=app_source,
            appname=app_name)\
            .exclude(version_number=None)

        # Sort available versions.
        from packaging import version
        app_versions = sorted(app_versions, key = lambda av : version.parse(av.version_number))

        # Display.
        print("Available versions:")
        for av in app_versions:
            # Show the app source, name, and version (but not if they were specified
            # as filters on the command line --- don't be redundnat).
            fields_to_show = []
            if not options["app_source"]: fields_to_show.append(app_source.slug)
            if not options["app_name"]: fields_to_show.append(av.appname)
            fields_to_show.append(av.version_number)

            # If the version is the actual version of the Project, indicate that.
            if av == project.root_task.module.app:
                fields_to_show.append("(current version)")
            
            else:
                # Test if the app can be safely upgraded. If not, indicate that in the output.
                if self.is_safe_upgrade(project, av) is not True:
                    fields_to_show.append("(incompatible)")
            print(" ".join(fields_to_show))

    @transaction.atomic
    def upgrade_app(self, project, options):
        # Get the current AppVersion.
        old_app = project.root_task.module.app

        # Get the target AppVersion.
        new_app = AppVersion.objects.get(
            source__slug=options["app_source"],
            appname=options["app_name"],
            version_number=options["app_version"])

        # Check that it is safe to upgrade to it.
        changed = self.is_safe_upgrade(project, new_app)
        if changed is not True:
            print("The compliance app has incompatible changes with the current app.")
            print(changed)
            return

        # Do the upgrade.

        # Get the Modules in use by this Project, and make a mapping from name to module,
        old_modules = Module.objects.filter(task__project=project).distinct()
        old_modules = {
            m.module_name: m
            for m in old_modules
        }

        # Get the corresponding Modules in the new app, and make a mapping.
        new_modules = new_app.modules.filter(module_name__in=old_modules.keys())
        new_modules = {
            m.module_name: m
            for m in new_modules
        }

        # Every task in the Project is updated to point to the corresponding Module
        # in the new app. This is optmized to do one database statement per Module
        # in use by the Task, which is slightly better than doing one statement per
        # Task, since multiple Tasks within the Project might use the same Module.
        # It would be even faster to use bulk_update added in Django 2.2 (https://docs.djangoproject.com/en/3.1/ref/models/querysets/#bulk-update).
        for m in old_modules.keys():
            Task.objects\
                .filter(project=project,
                        module=old_modules[m])\
                .update(module=new_modules[m])

        # Additionally, each TaskAnswer is updated to point to the corresponding
        # ModuleQuestion in the new app.

        # Get the ModuleQuestions in use by this Project, and make a mapping from
        # (module name, question key) to ModuleQuestion,
        old_module_questions = ModuleQuestion.objects\
            .select_related('module')\
            .filter(taskanswer__task__project=project).distinct()
        old_module_questions = {
            (q.module.module_name, q.key): q
            for q in old_module_questions
        }

        # Get the corresponding ModuleQuestionss in the new app, and make a similar mapping.
        new_module_questions = ModuleQuestion.objects\
            .select_related('module')\
            .filter(module__app=new_app)
        new_module_questions = {
            (q.module.module_name, q.key): q
            for q in new_module_questions
        }

        # Do the replacements. This is optmized to do one database statement per
        # ModuleQuestion that has been answered in the Task, which is slightly
        # better than doing one statement per TaskAnswer, since a ModuleQuestion
        # might be answered multiple times within a Project if the Project contains
        # multiple Tasks for the same Module. See the comment about using bulk_update
        # above.
        for key in old_module_questions.keys():
            TaskAnswer.objects\
                .filter(task__project=project,
                        question=old_module_questions[key])\
                .update(question=new_module_questions[key])
            print("Updating {}".format(new_module_questions[key]))
        print("Update complete.")

    def is_safe_upgrade(self, project, new_app):
        # A Project can be upgraded to a new app if every Module that has been started
        # in the Project corresponds to a Module in the new app *and* the new Module
        # has not changed in an incompatible way.

        old_app = project.root_task.module.app

        # Get the Modules in use by this Project, and make a mapping from name to module,
        old_modules = Module.objects.filter(task__project=project).distinct()
        old_modules = {
            m.module_name: m
            for m in old_modules
        }

        # Get the corresponding Modules in the new app, and make a mapping.
        new_modules = new_app.modules.filter(module_name__in=old_modules.keys())
        new_modules = {
            m.module_name: m
            for m in new_modules
        }

        # Check each module in use.
        for module_name, old_module in old_modules.items():
            if module_name not in new_modules:
                # Module must exist in the new app version to be compatible.
                return "The module {} does not exist in the new app.".format(module_name)
            else:
                new_module = new_modules[module_name]

                # Get the 'spec' which is the Python representation of the
                # YAML module data. Clone it (dict(...)).
                spec = dict(new_module.spec)

                # Put back information that we move out when we load it into the database
                # that is_module_changed expects to be there.
                spec["questions"] = [q.spec for q in new_module.questions.all()]

                changed = is_module_changed(old_module, new_app.source, spec)
                if changed in (None, False):
                    # 'None' signals no changes. 'False' means no incompatible changes.
                    pass
                else:
                    # There is an incompatible change. 'changed' holds a string describing
                    # the issue.
                    return changed

        # The upgrade is safe.
        return True
