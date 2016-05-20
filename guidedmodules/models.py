from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

from questions import Module, ModuleAnswers
from siteapp.models import User, Project, ProjectMembership

class Task(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, help_text="The Project that this Task is a part of, or empty for Tasks that are just directly owned by the user.")
    editor = models.ForeignKey(User, help_text="The user that has primary responsibility for completing this Task.")
    module_id = models.CharField(max_length=128, help_text="The ID of the module being completed.")

    title = models.CharField(max_length=256, help_text="The title of this Task. If the user is performing multiple tasks for the same module, this title would distiguish the tasks.")
    notes = models.TextField(blank=True, help_text="Notes set by the user about why they are completing this task.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="If 'deleted' by a user, the date & time the Task was deleted.")

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    invitation_history = models.ManyToManyField('siteapp.Invitation', blank=True, help_text="The history of accepted invitations that had this Task as a target.")

    class Meta:
        index_together = [
            ('project', 'editor', 'module_id'),
        ]

    def __str__(self):
        # For the admin.
        return self.title + " (" + self.module_id + ")"

    def __repr__(self):
        # For debugging.
        return "<Task [%d] %s %s>" % (self.id, self.title[0:30], repr(self.project))

    @staticmethod
    def has_completed_task(user, module_id):
        task = Task.get_task_for_module(user, module_id, create=False)
        return task and task.is_finished()

    @staticmethod
    def get_task_for_module(user, module_id, create=True):
        # Gets a task given a module_id. Use only with system modules
        # where a user can only have one Task for the module.

        filters = {
            "editor": user,
            "module_id": module_id,
            "project": None,
            "deleted_at": None,
        }

        if not create:
            # Check for existence first. If none exists, return None.
            return Task.objects.filter(**filters).first()

        task, isnew = Task.objects.get_or_create(**filters)
        if isnew:
            task.title = task.load_module().title
            task.save()
        return task

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/%d/%s" % (self.id, slugify(self.title))

    def load_module(self):
        from questions import Module
        return Module.load(self.module_id)

    def get_answers(self):
        m = self.load_module()
        answered = { }
        for q in self.questions.all():
            # Get the latest TaskAnswer instance for this TaskQuestion,
            # if there is any (there should be).
            a = q.get_answer()
            if not a:
                continue

            # If this question type is "module", its answer value is stored
            # differently --- and it is a Task instance.
            if m.questions_by_id[q.question_id].type == "module":
                if a.answered_by_task_id:
                    answered[q.question_id] = a.answered_by_task.get_answers()
            
            # Some answers store None to reflect that an answer has been
            # explicitly cleared. Don't pull those into the returned
            # dict -- they're not answers for the purposes of a Module.
            elif a.value:
                answered[q.question_id] = a.value

        return ModuleAnswers(m, answered)

    def can_transfer_owner(self):
        return self.project is not None

    def is_started(self):
        return self.questions.exists()

    def is_finished(self):
        return self.load_module().next_question(self.get_answers()) == None

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
            )

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

    def get_output(self, answers=None):
        if not answers:
            answers = self.get_answers()
        return answers.module.render_output(answers, {
            "project": self.project.title if self.project else None,
        })

    def is_answer_to_unique(self):
        # Is this Task a submodule of exactly one other Task?
        # We'd normally check len(self.is_answer_to.all()). But because we use TaskAnswers
        # to store the history of answers to a TaskQuestion, the uniqueness is on the
        # TaskQuestion... And then we want to return the current answer for that TaskQuestion.
        qs = TaskQuestion.objects.filter(answers__answered_by_task=self).distinct()
        if len(qs) == 1:
            return qs.first().get_answer()
        return None

class TaskQuestion(models.Model):
    task = models.ForeignKey(Task, related_name="questions", help_text="The Task that this TaskQuestion is a part of.")
    question_id = models.CharField(max_length=128, help_text="The ID of the question (within the Task's module) that this TaskQuestion represents.")

    notes = models.TextField(blank=True, help_text="Notes entered by editors working on this question.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('task', 'question_id')]

    def __str__(self):
        # For the admin.
        return self.get_question().title + " | " + self.task.title + " (" + self.task.module_id + "." + self.question_id + ")"

    def __repr__(self):
        # For debugging.
        return "<TaskQuestion %s in %s>" % (self.question_id, repr(self.task))

    def get_absolute_url(self):
        from urllib.parse import quote
        return self.task.get_absolute_url() + "?q=" + quote(self.question_id)

    def get_question(self):
        return self.task.load_module().questions_by_id[self.question_id]

    def get_answer(self):
        # The current answer is the one with the highest primary key.
        return self.answers.order_by('-id').first()

    def get_history(self):
        from discussion.models import reldate

        history = []

        # Get the answers. Their serial order follows their primary
        # key. We just want to know which was first so that we can
        # display different text.
        import html
        for i, answer in enumerate(self.answers.order_by('id')):
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


class TaskAnswer(models.Model):
    question = models.ForeignKey(TaskQuestion, related_name="answers", help_text="The TaskQuestion that this is an aswer to.")

    answered_by = models.ForeignKey(User, help_text="The user that provided this answer.")
    value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")
    answered_by_task = models.ForeignKey(Task, blank=True, null=True, related_name="is_answer_to", help_text="A Task that supplies the answer for this question.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this TaskAnswer.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __repr__(self):
        # For debugging.
        return "<TaskAnswer %s>" % (repr(self.question),)

    @property
    def is_answered(self):
        return bool(self.value or self.answered_by_task)

    def is_latest(self):
        # Is this the most recent --- the current --- answer for a TaskQuestion.
        return self.question.get_answer() == self

    def get_answer_display(self):
        return repr(self.value or self.answered_by_task)

