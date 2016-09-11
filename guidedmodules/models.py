from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

from collections import OrderedDict

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

    @property
    def title(self):
        return self.spec["title"]

    def get_questions(self):
        # Return the ModuleQuestions in definition order.
        return list(self.questions.order_by('definition_order'))

    @staticmethod
    def BuildNetworkDiagram(start_nodes, config):
        # Build a network diagram by recursively evaluating
        # node edges.
        from graphviz import Digraph
        g = Digraph()
        seen_nodes = set()
        stack = list(start_nodes)
        node_id = lambda node : str((type(node), node.id))
        while len(stack) > 0:
            # pop the next node
            node = stack.pop()
            if node in seen_nodes: continue # already did this node
            seen_nodes.add(node) # mark as visited

            # Create the node.
            g.node(
                node_id(node),
                label=config[type(node)]['label'](node),
                **config[type(node)]['attrs'](node))

            # Create the edges.
            edges = config[type(node)]['edges'](node)
            for edge_type, nodes in edges.items():
                for n in nodes:
                    g.edge(node_id(node), node_id(n), label=edge_type)
                    stack.append(n)
        
        if not seen_nodes:
            return None
        
        svg = g.pipe(format='svg')

        # strip off <? xml ... <!DOCTYPE ...
        import re
        svg = re.search(b"<svg .*", svg, re.S).group(0)
        return svg

    def module_usage_hierarchy(self):
        # For the admin.
        return Module.BuildNetworkDiagram(
            [self],
            {
                Module: {
                    "label": lambda node : str(node),
                    "edges": lambda node : { "answer-to": node.is_type_of_answer_to.all() },
                    "attrs": lambda node : { "color": "red" },
                },
                ModuleQuestion: {
                    "label": lambda node : node.key,
                    "edges": lambda node : { "in": [node.module] },
                    "attrs": lambda node : { "color": "blue" },
                }
            })

    def questions_dependencies(self):
        # For the admin.
        from .module_logic import get_questions_used_in_output, get_question_dependencies_with_type
        def get_question_dependencies(node):
            ret = { }
            for edge_type, n2 in get_question_dependencies_with_type(node):
                ret.setdefault(edge_type, []).append(n2)
            return ret
        return Module.BuildNetworkDiagram(
            get_questions_used_in_output(self),
            {
                ModuleQuestion: {
                    "label": lambda node : node.key,
                    "edges": lambda node : get_question_dependencies(node),
                    "attrs": lambda node : { },
                }
            })

class ModuleQuestion(models.Model):
    module = models.ForeignKey(Module, related_name="questions", on_delete=models.PROTECT, help_text="The Module that this ModuleQuestion is a part of.")
    key = models.SlugField(max_length=100, help_text="A slug-like identifier for the question.")

    definition_order = models.IntegerField(help_text="An integer giving the order in which this question is defined by the Module.")
    spec = JSONField(help_text="Module definition data.")
    answer_type_module = models.ForeignKey(Module, blank=True, null=True, related_name="is_type_of_answer_to", on_delete=models.PROTECT, help_text="For module and module-set typed questions, this is the Module that Tasks that answer this question must be for.")

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="The Project that this Task is a part of, or empty for Tasks that are just directly owned by the user.")
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
        # For the admin, notification strings.
        return self.title

    def __repr__(self):
        # For debugging.
        return "<Task [%d] %s %s>" % (self.id, self.title[0:30], repr(self.project))

    @staticmethod
    @transaction.atomic
    def create(parent_task_answer=None, **kwargs):
        # Creates a Task and also creates the required task-create
        # instrumentation event.

        # Create the task.
        task = Task.objects.create(**kwargs)

        # If the question that this task is answering has some "pass"
        # variables, create some answers with pre-set references.
        for pass_qid, pass_reference in \
              parent_task_answer.question.spec.get("pass", {}).items():

            # Find the TaskAnswer that a reference is being created to.
            # The pass_reference is a dot-delimited path through question
            # IDs to a TaskAnswer.
            ref_task = parent_task_answer.task
            ref = None
            for i, qid in enumerate(pass_reference.split(".")):
                # Follow the next step to get the next TaskAnswer.
                
                if ref_task is None:
                    raise ValueError("The pass specification %s is invalid because %s does not refer to a module-type question."
                        % (pass_reference, ".".join(pass_reference.split(".")[0:i])))
                
                try:
                    q = ref_task.module.questions.get(key=qid)
                except ModuleQuestion.DoesNotExist:
                    raise ValueError("The pass specification %s is invalid because %s refers to module %s which does not have a question whose id is %s."
                        % (pass_reference, ".".join(pass_reference.split(".")[0:i]) or "the context", ref_task.module, pass_qid))

                ref = TaskAnswer.objects.filter(task=ref_task, question=q).first()
                if not ref:
                    # A question on the path is unanswered --- just skip
                    # creating the reference.
                    break

                # If this TaskAnswer refers to another task, then we can take
                # a further step in the next iteration. Otherwise, no further
                # iterations are possible.
                ref_task = ref.get_current_answer().answered_by_task.first()

            if ref:
                # The referenced TaskAnswer exists. Create the reference.
                ans, _ = TaskAnswer.objects.get_or_create(
                    task=task,
                    question=task.module.questions.get(key=pass_qid),
                )
                TaskAnswerHistory.objects.create(
                    taskanswer=ans,
                    answered_by=kwargs["editor"],
                    stored_value=ref.get_current_value(),
                    answered_by_reference=ref)

        # Add instrumentation event.
        InstrumentationEvent.objects.create(
            user=kwargs["editor"],
            event_type="task-create",
            module=task.module,
            project=task.project,
            task=task,
            answer=parent_task_answer, # the TaskAnswer that the new Task is an answer to
        )

        return task

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/%d/%s" % (self.id, slugify(self.title))

    def get_absolute_url_to_question(self, question):
        # The project root task displays at different URLs.
        if self == self.project.root_task:
            from django.utils.text import slugify
            return self.project.get_absolute_url() + "#tab=" + slugify(question.spec.get("tab", ""))
        else:
            import urllib.parse
            return self.get_absolute_url() + "?" + urllib.parse.urlencode({"q": question.key })

    def get_answers(self):
        # Return a ModuleAnswers instance that wraps this Task and its Pythonic answer values.
        # The internal dict of answers is ordered to preserve the question definition order.
        answered = OrderedDict()
        for q in self.answers.all().order_by("question__definition_order"):
            # Get the latest TaskAnswerHistory instance for this TaskAnswer,
            # if there is any (there should be). If the answer is marked as
            # cleared, then treat as if it had not been answered.
            a = q.get_current_answer()
            if not a or a.cleared:
                continue

            # Get the value of that answer.
            answered[q.question.key] = a.get_value()

        return ModuleAnswers(self.module, self, answered)

    def can_transfer_owner(self):
        return not self.project.is_account_project

    def is_started(self):
        return self.answers.exists()

    def is_finished(self):
        # Check that all questions that need an answer have
        # an answer, and that no required questions have been
        # skipped.
        from .module_logic import next_question
        return next_question(self.get_answers(), required=True) == None

    def get_status_display(self):
        # Is this task done?
        if not self.is_finished():
            return "In Progress, last edit " + self.updated.strftime("%x %X")
        else:
            return "Finished on " + self.updated.strftime("%x %X")

    @staticmethod
    def get_all_tasks_readable_by(user, org):
        # symmetric with has_read_priv
        return Task.objects.filter(
            models.Q(editor=user) | models.Q(project__members__user=user),
            project__organization=org,
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

    def get_invitation_verb_inf(self, invitation):
        if invitation.target_info.get("what") == "editor":
            return "to take over editing"
        else:
            # invitation.target was initially a Project but upon
            # being accepted it was rewritten to be this task
            return "to begin editing"

    def get_invitation_verb_past(self, invitation):
        if invitation.target_info.get("what") == "editor":
            return "became the editor of"
        else:
            # invitation.target was initially a Project but upon
            # being accepted it was rewritten to be this task
            return "began"

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
        return self.get_absolute_url()

    def get_open_invitations(self, user):
        # Return the open Invitations for transferring task ownership
        # elsewhere, sent from the user.
        from siteapp.models import Invitation
        return Invitation.get_for(self).filter(from_user=user)

    def get_notification_watchers(self):
        return self.project.get_members()

    def render_title(self):
        import jinja2
        try:
            return render_content(
                {
                    "template": self.module.spec["instance-name"],
                    "format": "text",
                },
                self.get_answers(),
                "text"
            )
        except (KeyError, jinja2.TemplateError):
            return self.module.title

    def render_introduction(self):
        return render_content(
            self.module.spec.get("introduction", ""),
            ModuleAnswers(self.module, self, {}),
            "html"
        )

    def render_question_prompt(self, question):
        return render_content(
            {
                "template": question.spec["prompt"],
                "format": "markdown",
            },
            self.get_answers(),
            "html"
        )

    def render_question_title(self, question):
        return render_content(
            {
                "template": question.spec["title"],
                "format": "markdown",
            },
            self.get_answers(),
            "html"
        )

    def render_output_documents(self, answers=None, hard_fail=True):
        if answers is None:
            answers = self.get_answers()
        return answers.render_output({}, hard_fail=hard_fail)

    def render_snippet(self):
        snippet = self.module.spec.get("snippet")
        if not snippet: return None
        return render_content(
            snippet,
            self.get_answers(),
            "html",
        )

    def get_subtask(self, question_id):
        return self.get_or_create_subtask(None, question_id, create=False)

    @transaction.atomic
    def get_or_create_subtask(self, user, question_id, create=True):
        # For "module" type questions, creates a sub-Task for the question,
        # or if the question has already been answered then returns its
        # subtask.
        #
        # For "module-set" type questions, creates a new sub-Task and appends
        # it to the set of Tasks that answer the question.

        # Get the ModuleQuestion from the question_id.
        q = self.module.questions.get(key=question_id)

        # Get or create a TaskAnswer for that question.
        if create:
            ans, is_new = self.answers.get_or_create(question=q)
        else:
            ans = self.answers.get(question=q)
        
        # Get or create a TaskAnswerHistory for that TaskAnswer. For
        # "module"-type questions that have a sub-Task already, just
        # return the existing sub-Task.
        ansh = ans.get_current_answer()
        if q.spec["type"] == "module" and ansh and ansh.answered_by_task.count():
            # We'll re-use the subtask.
            return ansh.answered_by_task.first()

        elif not create:
            return None

        else:
            # There is no Task yet (for "module"-type questions) or
            # we're creating and appending a new task. Create the Task.
            task = Task.create(
                parent_task_answer=ans,
                project=self.project,
                editor=user,
                module=q.answer_type_module,
                title=q.answer_type_module.title)

            # Create a new TaskAnswerHistory instance. We never modify
            # existing instances!
            prev_ansh = ansh
            ansh = TaskAnswerHistory.objects.create(
                taskanswer=ans,
                answered_by=user,
                stored_value=None)

            # For "module-set"-type questions, copy in the previous set
            # of answers.
            if prev_ansh:
                for t in prev_ansh.answered_by_task.all():
                    ansh.answered_by_task.add(t)

            # Add the new task.
            ansh.answered_by_task.add(task)

            return task

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
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="answers", help_text="The Task that this TaskAnswer is a part of.")
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

    def get_current_value(self):
        a = self.get_current_answer()
        if a is None: return None
        return a.get_value()

    def get_history(self):
        from discussion.models import reldate

        history = []

        # Get the answers. Their serial order follows their primary
        # key. We just want to know which was first so that we can
        # display different text.
        import html
        is_cleared = True
        for i, answer in enumerate(self.answer_history.order_by('id')):
            if answer.cleared:
                vp = "cleared the answer"
                is_cleared = True
            elif self.question.spec["type"] == "interstitial":
                # answer/skip doesn't make sense here
                vp = "acknowledged this page"
                is_cleared = False
            elif answer.get_value() is None:
                vp = "skipped the question"
                is_cleared = False
            elif is_cleared:
                vp = "answered the question"
                is_cleared = False
            else:
                vp = "changed the answer"
                is_cleared = False

            # get a dict with information about the user
            who = answer.answered_by.render_context_dict(self.task.project.organization)

            history.append({
                "type": "event",
                "date": answer.created,
                "html":
                    ("<a href='javascript:alert(\"Profile link here.\")'>%s</a> " 
                    % html.escape(who['name']))
                    + vp + ".",
                "who": who,
                "who_is_in_text": True,
                "notification_text": str(answer.answered_by) + " " + vp + "."
            })

        # Sort.
        history.sort(key = lambda item : item["date"])

        # render events for easier client-side processing
        for item in history:
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
    taskanswer = models.ForeignKey(TaskAnswer, related_name="answer_history", on_delete=models.CASCADE, help_text="The TaskAnswer that this is an aswer to.")

    answered_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user that provided this answer.")

    stored_value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")
    answered_by_task = models.ManyToManyField(Task, blank=True, related_name="is_answer_to", help_text="A Task or Tasks that supplies the answer for this question (of type 'module' or 'module-set').")
    answered_by_file = models.FileField(upload_to='q/files', blank=True, null=True)
    cleared = models.BooleanField(default=False, help_text="Set to True to indicate that the user wants to clear their answer. This is different from a null-valued answer, which means not applicable/don't know/skip.")
    answered_by_reference = models.ForeignKey(TaskAnswer, blank=True, null=True, on_delete=models.SET_NULL, help_text="The answer to this question is determined by looking at the value of the current answer to the referenced question.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this TaskAnswerHistory.")

    thumbnail = models.FileField(upload_to='q/thumbnails', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __repr__(self):
        # For debugging.
        return "<TaskAnswerHistory %s>" % (repr(self.question),)

    def is_latest(self):
        # Is this the most recent --- the current --- answer for a TaskAnswer.
        return self.taskanswer.get_current_answer() == self

    def get_value(self):
        if self.cleared:
            raise RuntimeError("get_value cannot be called on a cleared answer")

        # If this answer found through a reference to another answer,
        # then recursively get the value. Update our cached copy if
        # the value has changed.
        # TODO: Prevent circular references from creating infinite recursion.
        if self.answered_by_reference:
            ans = self.answered_by_reference.get_current_answer()
            if ans:
                value = ans.get_value()
                if value != self.stored_value:
                    self.stored_value = value
                    self.save(update_fields=['stored_value'])
                return value

        # Get the ModuleQuestion that defines the type of the question
        # that this answer is for.
        q = self.taskanswer.question

        # If this question type is "module" or "module-set", its answer
        # is stored in the answered_by_task M2M field and the stored_value
        # field is not used. The return value is a ModuleAnswers instance.
        if q.spec["type"] == "module":
            t = self.answered_by_task.first()
            if not t:
                # The question is skipped.
                return None
            # Fetch value recursively (TODO: Prevent circular references that
            # lead to infinite recursion.)
            return t.get_answers()

        elif q.spec["type"] == "module-set":
            return [t.get_answers() for t in self.answered_by_task.all()]

        # The "file" question type is answered by a blob that is uploaded
        # by the user. The stored_value field is not used. Instead the
        # answered_by_file field points to the blob. The returned data is
        # a dict about the blob.
        elif q.spec["type"] == "file":
            # Get the Django File object instance.
            blob = self.answered_by_file
            if not blob.name:
                # Question was skipped.
                return None

            # Get the dbstorage.models.StoredFile instance which holds
            # an auto-detected mime type.
            from dbstorage.models import StoredFile
            sf = StoredFile.objects.get(path=blob.name)
            return {
                "url": settings.SITE_ROOT_URL + blob.url,
                "size": blob.size,
                "type": sf.mime_type,
            }
        
        # For all other question types, the value is stored in the stored_value
        # field.
        else:
            return self.stored_value

    def get_answer_display(self):
        if self.cleared:
            return "[answer cleared]"
        if self.taskanswer.question.spec["type"] in ("module", "module-set"):
            return repr(self.answered_by_task.all())
        else:
            return repr(self.get_value())

class InstrumentationEvent(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    event_time = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=32)
    event_value = models.FloatField(null=True)

    module = models.ForeignKey(Module, blank=True, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(ModuleQuestion, blank=True, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.SET_NULL)
    answer = models.ForeignKey(TaskAnswer, blank=True, null=True, on_delete=models.SET_NULL)

    extra = JSONField(help_text="Additional un-indexed data.")

    class Meta:
        index_together = [
            ('event_type', 'event_time'),
            ('project', 'event_type', 'event_time'),
            ('module', 'event_type', 'event_time'),
        ]
