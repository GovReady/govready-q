from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

from .module_logic import ModuleAnswers, render_content
from siteapp.models import User, Project, ProjectMembership

class Module(models.Model):
    key = models.SlugField(max_length=100, db_index=True, help_text="A slug-like identifier for the Module.")

    visible = models.BooleanField(default=True, db_index=True, help_text="Whether the Module is offered to users.")
    superseded_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, help_text="When a Module is superseded by a new version, this points to the newer version.")

    spec = JSONField(help_text="Module definition data.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin.
        return "%s [%d]" % (self.key, self.id)

    def __repr__(self):
        # For debugging.
        return "<Module [%d] %s%s %s>" % (self.id, "" if not self.superseded_by else "(old) ", self.key, self.spec["title"][0:30])

    @staticmethod
    def get_startable_modules():
        return Module.objects.filter(visible=True, superseded_by=None)

    @property
    def title(self):
        return self.spec["title"]

    def get_questions(self):
        # Return the ModuleQuestions in definition order.
        return list(self.questions.order_by('definition_order'))

class ModuleQuestion(models.Model):
    module = models.ForeignKey(Module, related_name="questions", on_delete=models.PROTECT, help_text="The Module that this ModuleQuestion is a part of.")
    key = models.SlugField(max_length=100, help_text="A slug-like identifier for the question.")

    definition_order = models.IntegerField(help_text="An integer giving the order in which this question is defined by the Module.")
    spec = JSONField(help_text="Module definition data.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [("module", "key")]

    def __str__(self):
        return "%s[%d].%s" % (self.module.key, self.module.id, self.key)

    def __repr__(self):
        # For debugging.
        return "<ModuleQuestion [%d] %s.%s (%s)>" % (self.id, self.module.key, self.key, repr(self.module))

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, help_text="The Project that this Task is a part of, or empty for Tasks that are just directly owned by the user.")
    editor = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user that has primary responsibility for completing this Task.")
    module = models.ForeignKey(Module, on_delete=models.PROTECT, help_text="The Module that this Task is answering.")

    title = models.CharField(max_length=256, help_text="The title of this Task. If the user is performing multiple tasks for the same module, this title would distiguish the tasks.")
    notes = models.TextField(blank=True, help_text="Notes set by the user about why they are completing this task.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="If 'deleted' by a user, the date & time the Task was deleted.")

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    invitation_history = models.ManyToManyField('siteapp.Invitation', blank=True, help_text="The history of accepted invitations that had this Task as a target.")

    class Meta:
        index_together = [
            ('project', 'editor', 'module'),
        ]

    def __str__(self):
        # For the admin.
        return self.title + " (" + str(self.module) + ")"

    def __repr__(self):
        # For debugging.
        return "<Task [%d] %s %s>" % (self.id, self.title[0:30], repr(self.project))

    @staticmethod
    def has_completed_task(user, project, module_id):
        task = Task.get_task_for_module(user, project, module_id, create=False)
        return task and task.is_finished()

    @staticmethod
    def get_task_for_module(user, project, module_id, create=True):
        # Gets a task given a module_id. Use only for modules that the
        # user can only have one of (within a project).

        filters = {
            "editor": user,
            "project": project,
            "deleted_at": None,
        }

        # Check for existence first. If none exists, return None.
        # Because of module versioning, we're looking for tasks
        # that are for any version of a particular module.
        task = Task.objects.filter(module__key=module_id, **filters).first()
        if not create or task:
            # Return the task if we found one, or None if the caller
            # doesn't want us to create one.
            return task

        # Create a new task. Use the most recent version of the module.
        m = Module.objects.get(key=module_id, superseded_by=None)
        task = Task.objects.create(
            module=m,
            title=m.title,
            **filters)
        return task

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/%d/%s" % (self.id, slugify(self.title))

    def get_answers(self):
        answered = { }
        for q in self.answers.all():
            # Get the latest TaskAnswerHistory instance for this TaskAnswer,
            # if there is any (there should be).
            a = q.get_current_answer()
            if not a:
                continue

            # If this question type is "module", its answer value is stored
            # differently --- and it is a Task instance.
            if q.question.spec["type"] == "module":
                if a.answered_by_task_id:
                    answered[q.question.key] = a.answered_by_task.get_answers()
            
            # Some answers store None to reflect that an answer has been
            # explicitly cleared. Don't pull those into the returned
            # dict -- they're not answers for the purposes of a Module.
            elif a.value:
                answered[q.question.key] = a.value

        return ModuleAnswers(self.module, answered)

    def can_transfer_owner(self):
        return not self.project.is_account_project

    def is_started(self):
        return self.answers.exists()

    def is_finished(self):
        from .module_logic import next_question
        return next_question(self.module, self.get_answers()) == None

    def get_status_display(self):
        # Is this task done?
        if not self.is_finished():
            return "In Progress, last edit " + self.updated.strftime("%x %X")
        else:
            return "Finished on " + self.updated.strftime("%x %X")

    @staticmethod
    def get_all_tasks_readable_by(user):
        # symmetric with has_read_priv
        return Task.objects.filter(
            models.Q(editor=user) | models.Q(project__members__user=user),
            deleted_at=None,
            ).distinct()

    def has_read_priv(self, user, allow_access_to_deleted=False):
        # symmetric get_all_tasks_readable_by has_read_priv
        if self.deleted_at and not allow_access_to_deleted:
            return False
        if self.has_write_priv(user, allow_access_to_deleted=allow_access_to_deleted):
            return True
        if ProjectMembership.objects.filter(project=self.project, user=user).exists():
            return True
        return False

    def has_write_priv(self, user, allow_access_to_deleted=False):
        if self.deleted_at and not allow_access_to_deleted:
            return False
        if self.editor == user:
            # The editor.
            return True
        if ProjectMembership.objects.filter(project=self.project, user=user, is_admin=True).exists():
            # An admin of the project.
            return True
        return False

    def get_invitation_purpose(self, invitation):
        if invitation.target_info.get("what") == "editor":
            return ("to take over editing <%s>" % self.title) \
                + (" and to join the project team" if invitation.into_project else "")
        else:
            return ("to begin editing <%s>" % self.title) \
                + (" and to join the project team" if invitation.into_project else "")

    def is_invitation_valid(self, invitation):
        # Invitation remains valid only if the user that sent it still
        # has write privs to the Task (i.e. task is not deleted, user
        # is the editor or an admin)
        return self.has_write_priv(invitation.from_user)

    def accept_invitation(self, invitation, add_message):
        # Make this user the new editor.
        self.editor = invitation.accepted_user
        self.save(update_fields=['editor'])
        add_message('You are now the editor for module %s.' % self.title)
        self.invitation_history.add(invitation)

    def get_invitation_redirect_url(self, invitation):
        return self.get_absolute_url() + "/start"

    def get_open_invitations(self, user):
        # Return the open Invitations for transferring task ownership
        # elsewhere, sent from the user.
        from siteapp.models import Invitation
        return Invitation.get_for(self).filter(from_user=user)

    def get_document_additional_context(self):
        return {
            "project": self.project.title if self.project else None,
        }

    def render_title(self):
        import jinja2
        try:
            return render_content(
                {
                    "template": self.module.spec["instance-name"],
                    "format": "text",
                },
                self.get_answers(),
                "text",
                self.get_document_additional_context()
            )
        except (KeyError, jinja2.TemplateError):
            return self.module.title

    def render_introduction(self):
        return render_content(
            self.module.spec.get("introduction", ""),
            ModuleAnswers(self.module, {}),
            "html",
            self.get_document_additional_context()
        )

    def render_question_prompt(self, question):
        return render_content(
            {
                "template": question.spec["prompt"],
                "format": "markdown",
            },
            self.get_answers(),
            "html",
            self.get_document_additional_context()
        )

    def get_output(self, answers=None):
        if not answers:
            answers = self.get_answers()
        return answers.render_output(self.get_document_additional_context())

    def is_answer_to_unique(self):
        # Is this Task a submodule of exactly one other Task?
        # We'd normally check len(self.is_answer_to.all()). But because we use TaskAnswerHistorys
        # to store the history of answers to a TaskAnswer, the uniqueness is on the
        # TaskAnswer... And then we want to return the current answer for that TaskAnswer.
        qs = TaskAnswer.objects.filter(answer_history__answered_by_task=self).distinct()
        if len(qs) == 1:
            return qs.first()
        return None

class TaskAnswer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, related_name="answers", help_text="The Task that this TaskAnswer is a part of.")
    question = models.ForeignKey(ModuleQuestion, on_delete=models.PROTECT, help_text="The question (within the Task's Module) that this TaskAnswer is answering.")

    notes = models.TextField(blank=True, help_text="Notes entered by editors working on this question.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('task', 'question')]

    def __str__(self):
        # For the admin.
        return str(self.question) + " | " + str(self.task)

    def __repr__(self):
        # For debugging.
        return "<TaskAnswer %s in %s>" % (repr(self.question), repr(self.task))

    def get_absolute_url(self):
        from urllib.parse import quote
        return self.task.get_absolute_url() + "?q=" + quote(self.question.key)

    def get_current_answer(self):
        # The current answer is the one with the highest primary key.
        return self.answer_history.order_by('-id').first()

    def get_history(self):
        from discussion.models import reldate

        history = []

        # Get the answers. Their serial order follows their primary
        # key. We just want to know which was first so that we can
        # display different text.
        import html
        for i, answer in enumerate(self.answer_history.order_by('id')):
            vp = ("answered the question" if i == 0 else "changed the answer")
            history.append({
                "type": "event",
                "date": answer.created,
                "html":
                    ("<a href='javascript:alert(\"Profile link here.\")'>%s</a> " 
                    % html.escape(str(answer.answered_by)))
                    + vp + ".",
                "who": answer.answered_by,
                "who_is_in_text": True,
                "notification_text": str(answer.answered_by) + " " + vp + "."
            })

        # Sort.
        history.sort(key = lambda item : item["date"])

        # render events for easier client-side processing
        for item in history:
            if "who" in item:
                item["who"] = item["who"].render_context_dict()

            item["date_relative"] = reldate(item["date"], timezone.now()) + " ago"
            item["date_posix"] = item["date"].timestamp()
            del item["date"] # not JSON serializable

        return history

    # required to attach a Discussion to it
    @property
    def project(self):
        return self.task.project

    # required to attach a Discussion to it
    @property
    def title(self):
        return self.question.spec["title"] + " - " + self.task.title

class TaskAnswerHistory(models.Model):
    taskanswer = models.ForeignKey(TaskAnswer, related_name="answer_history", on_delete=models.PROTECT, help_text="The TaskAnswer that this is an aswer to.")

    answered_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user that provided this answer.")
    value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")
    answered_by_task = models.ForeignKey(Task, blank=True, null=True, related_name="is_answer_to", on_delete=models.PROTECT, help_text="A Task that supplies the answer for this question.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this TaskAnswerHistory.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __repr__(self):
        # For debugging.
        return "<TaskAnswerHistory %s>" % (repr(self.question),)

    @property
    def is_answered(self):
        return bool(self.value or self.answered_by_task)

    def is_latest(self):
        # Is this the most recent --- the current --- answer for a TaskAnswer.
        return self.taskanswer.get_current_answer() == self

    def get_answer_display(self):
        return repr(self.value or self.answered_by_task)

