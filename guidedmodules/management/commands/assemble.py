# This management command provides a command-line interface
# GovReady-Q. It loads a single compliance app into the
# database, answers its questions (possibly by starting other
# compliance apps and answering their questions), saves all
# of its output documents to an output directory.
#
# A throw-away test database is used so that this command
# cannot see any existing user data and database changes are
# not persistent. However, it would not be advisable to run
# this command on a production system.

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.crypto import get_random_string

from siteapp.models import User, Organization, Project
from guidedmodules.models import AppSource, Task, TaskAnswer
from guidedmodules.module_logic import ModuleAnswers

import os
import os.path
import rtyaml

import termcolor

LOG_COLORS = { "INFO": "white", "OK": "green", "WARN": "yellow", "ERROR": "red" }
LOG_SYMBOLS = { "INFO": " ", "OK": "🗸", "WARN": "!", "ERROR": "✗" }
LOG_NAMES = { "WARN": "warning", "ERROR": "error" }

class Command(BaseCommand):
    help = 'Starts compliance apps using a YAML driver file that specifies apps and data.'

    def __init__(self):
        self.indent = 0
        self.logcounts = { }

    def add_arguments(self, parser):
        parser.add_argument('data.yaml', type=str)
        parser.add_argument('outdir', type=str)

    def handle(self, *args, **options):
        self.StartApps(options['data.yaml'], options["outdir"])

    # Show colored log output and count the number of warnings and errors.
    def log(self, level, message):
        color = LOG_COLORS[level]
        symbol = LOG_SYMBOLS[level]
        print((" "*self.indent) + termcolor.colored(symbol, color), message)
        self.logcounts[level] = self.logcounts.get(level, 0) + 1

    def StartApps(self, fn, outdir):
        # Fixup Django settings. Turn DEBUG off. This might speed up
        # program execution if e.g. database queries are not logged.
        settings.DEBUG = False

        # Switch to the throw-away test database so no database records
        # we create in this command are persistent.
        from django.test.utils import setup_databases, teardown_databases
        dbinfo = setup_databases(True, False)

        try:
            # Create stub data structures that are required to do module logic
            # but that have no end-user-visible presence.
            self.dummy_org = Organization.objects.create(subdomain=get_random_string(12))
            self.dummy_user = User.objects.create(username=get_random_string(12))

            # Cache app sources and app instances as we load app data into the
            # database so that when sources and apps occur multiple times we
            # reuse the existing instances in the database.
            self.app_sources = { }
            self.app_instances = { }

            # Open the end-user data file.
            data = rtyaml.load(open(fn))

            # Start the app.
            basedir = os.path.dirname(fn)
            project = self.start_app(data.get("app"), basedir)

            if project: # no error
                # Fill in the answers.
                self.set_answers(project.root_task, data.get("questions", []), basedir)

                # Generate outputs.
                self.save_outputs(project, outdir)
        finally:
            # Clean up the throw-away test database.
            teardown_databases(dbinfo, 1)

        for level in ("WARN", "ERROR"):
            print(termcolor.colored("{} {}(s)".format(
                self.logcounts.get(level, 0),
                LOG_NAMES[level],
            ), LOG_COLORS[level]))

    def str_task(self, task):
        return "<#{}: {}>".format(task.id, task.title)

    def start_app(self, app, basedir):
        # Validate app info. It can be specified either as a string path
        # to a local copy of an app, or as a Python dict holding 'source'
        # and 'name' keys, where 'source' is the AppSource connection spec.
        if not isinstance(app, (dict, str)): raise ValueError("invalid data type")
        if isinstance(app, dict):
            if not isinstance(app.get("source"), dict): raise ValueError("invalid data type")
            if not isinstance(app.get("name"), str): raise ValueError("invalid data type")

        # Get an existing AppInstance if we've already created this app,
        # otherwise create a new AppInstance.
        key = rtyaml.dump(app)
        if key in self.app_instances:
            app_inst = self.app_instances[key]
        else:
            # Create a AppSource, or reuse if this source has been used before.

            if isinstance(app, str):
                # If given as a string, take the last directory name as the
                # app name and the preceding directories as the AppSource
                # connection path.
                spec = {
                    "type": "local",
                    "path": os.path.normpath(os.path.join(basedir, os.path.dirname(app))),
                }
                appname = os.path.basename(app)
            else:
                # Otherwise the 'source' and 'name' keys hold the source and app info.
                spec = app["source"]
                appname = app["name"]

            # If we've already created & cached the AppSource, use it.
            srckey = rtyaml.dump(spec)
            if srckey in self.app_sources:
                app_src = self.app_sources[srckey]

            # Create a new AppSource.
            else:
                app_src = AppSource.objects.create(
                    slug="source_{}_{}".format(len(self.app_sources), get_random_string(6)),
                    spec=spec,
                )
                self.app_sources[srckey] = app_src

            # Start an app.
            from guidedmodules.app_loading import load_app_into_database
            try:
                with app_src.open() as conn:
                    self.log("INFO", "Loading app {} from {}...".format(appname, app_src.get_description()))
                    app_inst = load_app_into_database(conn.get_app(appname))
            except Exception as e:
                self.log("ERROR", str(e))
                return None

            self.app_instances[key] = app_inst

        # Start the app --- make a Project object.
        module = app_inst.modules.get(module_name="app")
        project = Project.objects.create(organization=self.dummy_org)
        project.set_root_task(module, self.dummy_user)
        self.log("OK", "Started {} using {} from {}.".format(self.str_task(project.root_task), app_inst.appname, app_inst.source.get_description()))

        return project

    def set_answers(self, task, answers, basedir):
        # Fill in the answers for this task using the JSON data in answers,
        # which is a list of dicts that have "id" holding the question ID
        # and other fields. We call set_answer for all questions, even if
        # there is no user-provided answer, because some module-type questions
        # without protocols should be answered with a sub-Task anyway (see below).

        # Map the answers to a dict.
        if not isinstance(answers, list): raise ValueError("invalid data type")
        answers = { answer["id"]: answer for answer in answers
                    if isinstance(answer, dict) and "id" in answer }

        questions = task.module.questions.order_by('definition_order')
        if questions.count() == 0:
            return # don't emit anything more if no questions

        self.log("INFO", "Answering {}...".format(task))
        self.indent += 1
        try:
            not_answered = []
            for question in questions:
                if not self.set_answer(task, question, answers.get(question.key), basedir):
                    not_answered.append(question.key)
            if not_answered:
                self.log("WARN", "No answers were given for {} in {}.".format(", ".join(not_answered), self.str_task(task)))
        finally:
            self.indent -= 1

    def set_answer(self, task, question, answer, basedir):
        # Set the answer to the question for the given task.

        if question.spec["type"] == "module" and question.answer_type_module is not None:
            # If there is no answer provided, normally we leave
            # the answer blank. However, for module-type questions
            # with a module type (not a protocol), we should at least
            # *start* the sub-task with the module answer type, even if we
            # don't answer any of its questions, because it may be
            # a question-less module that only provides output documents.
            sub_task = task.get_or_create_subtask(self.dummy_user, question)
            # self.log("OK", "Answered {} with {}.".format(question.key, sub_task))
            if answer is not None:
                self.set_answers(sub_task, answer.get("questions", []), basedir)
                return True
            return False

        # If the question isn't answered, leave it alone.
        if answer is None:
            return False

        # Set an answer to the question.

        # Get the TaskAnswer record, which has the save_answer function.
        taskans, isnew = TaskAnswer.objects.get_or_create(task=task, question=question)
        
        if question.spec["type"] in ("module", "module-set"):
            # A module-type question with a protocol (if there was no protocol, it
            # was handled above) or a module-set question (with or without a protocol).

            if question.spec["type"] == "module":
                answers = [answer]
            else:
                answers = answer.get("answers", [])
            
            # Start the app(s).
            subtasks = []
            for answer in answers:
                if question.answer_type_module is not None:
                    # Start the sub-task.
                    subtasks.append(task.get_or_create_subtask(self.dummy_user, question))
                else:
                    # Start the app. The app to start is specified in the 'app' key.
                    if not isinstance(answer, dict): raise ValueError("invalid data type")
                    project = self.start_app(answer.get("app"), basedir)

                    if project is None:
                        return False # error

                    # Validate that the protocols match.
                    unimplemented_protocols = set(question.spec.get("protocol", [])) - set(project.root_task.module.spec.get("protocol", []))
                    if unimplemented_protocols:
                        # There are unimplemented protocols.
                        self.log("ERROR", "{} doesn't implement the protocol {} required to answer {}.".format(
                            project.root_task.module.app,
                            ", ".join(sorted(unimplemented_protocols)),
                            question.key
                        ))
                        return False

                    # Keep the root Task to be an answer to the question.
                    subtasks.append(project.root_task)

            # Save the answer.
            if taskans.save_answer(None, subtasks, None, self.dummy_user, "api"):
                self.log("OK", "Answered {} with {}.".format(
                    question.key,
                    ", ".join([self.str_task(t) for t in subtasks])))

                # Set answers of sub-task.
                for subtask, subtask_answers in zip(subtasks, answers):
                    self.set_answers(subtask, subtask_answers.get("questions", []), basedir)

                return True


        else:
            # This is a regular question type with YAML data holding the answer value.
            # Validate the value.
            from guidedmodules.answer_validation import validator
            try:
                value = validator.validate(question, answer["answer"])
            except ValueError as e:
                self.log("ERROR", "Answering {}: {}".format(question.key, e))
                return False

            # Save the value.
            if taskans.save_answer(value, [], None, self.dummy_user, "api"):
                self.log("OK", "Answered {} with {}.".format(question.key, repr(value)))
                return True

            # No change, somehow.
            return False

    def save_outputs(self, project, outdir):
        self.generate_task_outputs(project.root_task, outdir)

    def generate_task_outputs(self, task, path):
        # Generate this task's output documents.
        for i, doc in enumerate(task.render_output_documents()):
            self.save_output_document(i, doc, path)

        self.log("OK", "Wrote documents for " + self.str_task(task) + " to " + path + ".")

        try:
            # Run recursively on any module answers to questions.
            self.indent += 1
            for q, is_answered, a, value in task.get_answers().with_extended_info().answertuples.values():
                if isinstance(value, ModuleAnswers) and value.task:
                    self.generate_task_outputs(value.task, os.path.join(path, q.key))
        finally:
            self.indent -= 1

    def save_output_document(self, i, doc, path):
        os.makedirs(path, exist_ok=True)
        key = doc["id"] if ("id" in doc) else "{:05d}".format(i)
        for ext, format in (("html", "html"), ("md", "markdown")):
            if format in doc:
                fn = os.path.join(path, key + "." + ext)
                with open(fn, "w") as f:
                    f.write(doc[format])
