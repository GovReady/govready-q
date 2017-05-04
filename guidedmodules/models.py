from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

from collections import OrderedDict
import uuid

from .module_logic import ModuleAnswers, render_content, validator
from siteapp.models import User, Organization, Project, ProjectMembership

ModulePythonCode = { }

class ModuleSource(models.Model):
    namespace = models.CharField(max_length=200, unique=True, help_text="The namespace that modules loaded from this source are added into.")
    spec = JSONField(help_text="A load_modules ModuleRepository spec.")

    trust_javascript_assets = models.BooleanField(default=False, help_text="Are new Javascript static assets loaded from this source trusted to be served on our domain and run client side?")
    available_to_all = models.BooleanField(default=True, help_text="Turn off to restrict the Modules loaded from this source to particular organizations.")
    available_to_orgs = models.ManyToManyField(Organization, blank=True, help_text="If available_to_all is False, list the Organizations that can start projects defined by Modules provided by this ModuleSource.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __str__(self):
        # for the admin
        return self.namespace

    def get_description(self):
        if self.spec["type"] == "null":
            return "null source"
        if self.spec["type"] == "local":
            return "local filesystem at %s" % self.spec.get("path")
        if self.spec["type"] == "git":
            return self.spec.get("url")
        if self.spec["type"] == "github":
            return "github.com/%s" % self.spec.get("repo")

class Module(models.Model):
    source = models.ForeignKey(ModuleSource, help_text="The source of this module definition.")

    key = models.SlugField(max_length=100, db_index=True, help_text="A slug-like identifier for the Module.")

    visible = models.BooleanField(default=True, db_index=True, help_text="Whether the Module is offered to users.")
    superseded_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, help_text="When a Module is superseded by a new version, this points to the newer version.")

    spec = JSONField(help_text="Module definition data.")
    assets = models.ForeignKey('ModuleAssetPack', blank=True, null=True, help_text="A mapping from asset paths to ModuleAsset instances with the binary content of the asset.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        # For the admin.
        return "%s [%d]" % (self.key, self.id)

    def __repr__(self):
        # For debugging.
        return "<Module [%d] %s%s %s>" % (self.id, "" if not self.superseded_by else "(old) ", self.key, self.spec.get("title", "<No Title>")[0:30])

    @property
    def parent_path(self):
        return "/".join(self.key.split("/")[:-1])

    @property
    def title(self):
        return self.spec["title"]

    def get_questions(self):
        # Return the ModuleQuestions in definition order.
        return list(self.questions.order_by('definition_order'))

    def python_functions(self):
        # Run exec() on the Python source code stored in the spec, and cache the
        # globally defined functions, classes, and variables.
        global ModulePythonCode
        if self.id not in ModulePythonCode:
            exec(
                self.spec.get("python-module", ""),
                None, # default globals - TODO: Make this safe?
                ModulePythonCode.setdefault(self.id, {}) # put locals, i.e. global definitions, here
            )
        return ModulePythonCode[self.id]

    def export_json(self, serializer):
        # Exports this Module's metadata to a JSON-serializable Python data structure.
        # Called via siteapp.Project::export_json.
        from collections import OrderedDict
        return serializer.serializeOnce(
            self,
            "module:" + self.key, # a preferred key, doesn't need to be unique here
            lambda : OrderedDict([  # "lambda :" makes this able to be evaluated lazily
                ("key", self.key),
                ("created", self.created.isoformat()),
                ("modified", self.updated.isoformat()),
        ]))

    def get_static_asset_url(self, asset_path):
        if not self.assets:
            # No assets are defined for this Module, so just return the
            # path as it's probably an absolute URL.
            return asset_path

        # Look up the content_hash of the asset from its path.
        content_hash = self.assets.paths.get(asset_path)
        if not content_hash:
            # This is not an asset so let it through as it might be an
            # absolute URL.
            return asset_path

        # Look up the ModuleAsset based on the hash.
        asset = self.assets.assets.get(source=self.source, content_hash=content_hash)

        # Give the public URL of that asset.
        return asset.get_absolute_url()

    @staticmethod
    def BuildNetworkDiagram(start_nodes, config):
        # Build a network diagram by recursively evaluating
        # node edges.
        from graphviz import Digraph
        g = Digraph(name=config['name'])
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
                tooltip=config[type(node)]['tooltip'](node),
                **config[type(node)]['attrs'](node))

            # Create the edges.
            edges = config[type(node)]['edges'](node)
            for edge_type, nodes in edges.items():
                for n in nodes:
                    g.edge(
                        node_id(node),
                        node_id(n),
                        label=edge_type,
                        )
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
                'name': 'Module Usage',
                Module: {
                    "label": lambda node : str(node),
                    "edges": lambda node : { "answer-to": node.is_type_of_answer_to.all() },
                    "attrs": lambda node : { "color": "red" },
                    "tooltip": lambda node : node.spec['title'],
                },
                ModuleQuestion: {
                    "label": lambda node : node.key,
                    "edges": lambda node : { "in": [node.module] },
                    "attrs": lambda node : { "color": "blue" },
                    "tooltip": lambda node : node.spec['title'],
                }
            })

    def questions_dependencies(self):
        # For the admin.
        from .module_logic import get_all_question_dependencies, get_question_dependencies_with_type
        _, root_questions = get_all_question_dependencies(self)
        def get_question_dependencies(node):
            ret = { }
            for edge_type, n2 in get_question_dependencies_with_type(node):
                ret.setdefault(edge_type, []).append(n2)
            return ret
        return Module.BuildNetworkDiagram(
            root_questions,
            {
                'name': 'Question Dependencies',
                ModuleQuestion: {
                    "label": lambda node : node.key,
                    "edges": lambda node : get_question_dependencies(node),
                    "attrs": lambda node : { },
                    "tooltip": lambda node : node.spec['title'],
                }
            })


class ModuleAsset(models.Model):
    source = models.ForeignKey(ModuleSource, help_text="The source of the asset.")
    content_hash = models.CharField(max_length=64, help_text="A hash of the asset binary content, as provided by the source.")
    file = models.FileField(upload_to='guidedmodules/module-assets', help_text="The attached file.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('source', 'content_hash')]

    def get_absolute_url(self):
        return self.file.url


class ModuleAssetPack(models.Model):
    source = models.ForeignKey(ModuleSource, help_text="The source of these assets.")
    assets = models.ManyToManyField(ModuleAsset, help_text="The assets linked to this pack.")
    basepath = models.SlugField(max_length=100, help_text="The base path of all assets in this pack.")
    paths = JSONField(help_text="A dictionary mapping file paths to the content_hashes of assets included in the assets field of this instance.")
    total_hash = models.CharField(max_length=64, help_text="A SHA256 hash over the paths and the content_hashes of the assets.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('source', 'total_hash')]

    def set_total_hash(self):
        import hashlib, json
        m = hashlib.sha256()
        m.update(
            json.dumps({
                    "basepath": self.basepath,
                    "paths": self.paths,
                },
                sort_keys=True,
            ).encode("utf8")
        )
        self.total_hash = m.hexdigest()



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

    cached_is_finished = models.NullBooleanField(help_text="Cached value storing whether the Task is finished.")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, help_text="A UUID (a unique identifier) for this Task, used to synchronize Task content between systems.")

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
        task = Task.objects.create(**kwargs)

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

    def get_slug(self):
        from django.utils.text import slugify
        return slugify(self.title)

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/%d/%s" % (self.id, self.get_slug())

    def get_absolute_url_to_question(self, question):
        # The project root task displays at different URLs.
        if self == self.project.root_task:
            from django.utils.text import slugify
            return self.project.get_absolute_url() + "#tab=" + slugify(question.spec.get("tab", ""))
        else:
            import urllib.parse
            return self.get_absolute_url() + "/question/" + urllib.parse.quote(question.key)

    def get_answers(self, decryption_provider=None):
        # Return a ModuleAnswers instance that wraps this Task and its Pythonic answer values.

        # Since we track the history of answers to each question, we need to get the most
        # recent answer for each question. It's fastest if we pre-load the complete history
        # of every question rather than making a separate database call for each to find
        # its most recent answer. See TaskAnswer.get_current_answer().
        answers = list(
            TaskAnswerHistory.objects
                .filter(taskanswer__task=self)
                .order_by('-id')
                .select_related('taskanswer', 'taskanswer__task', 'taskanswer__question', 'answered_by')
                .prefetch_related('answered_by_task')
                )
        def get_current_answer(q):
            for a in answers:
                if a.taskanswer == q:
                    return a
            return None

        # Loop over all of the questions and fetch each's answer.
        # The internal dict of answers is ordered to preserve the question definition order.
        answered = OrderedDict()
        for q in self.answers.all()\
            .order_by("question__definition_order")\
            .select_related("question"):
            # Get the latest TaskAnswerHistory instance for this TaskAnswer,
            # if there is any (there should be). If the answer is marked as
            # cleared, then treat as if it had not been answered.
            a = get_current_answer(q) # faster than but equivalent to q.get_current_answer()
            if not a or a.cleared:
                continue

            # Get the value of that answer.
            answered[q.question.key] = a.get_value(decryption_provider=decryption_provider)

        return ModuleAnswers(self.module, self, answered)

    def can_transfer_owner(self):
        return not self.project.is_account_project

    def is_started(self):
        return self.answers.exists()

    def is_finished(self):
        # Check that all questions that need an answer have
        # an answer, and that no required questions have been
        # skipped.
        if self.cached_is_finished is None:
            self.cached_is_finished = len(self.get_answers().with_extended_info(required=True).can_answer) == 0
            self.save(update_fields=["cached_is_finished"])
        return self.cached_is_finished

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

    # INVITATION TARGET FUNCTIONS

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

    def get_invitation_interstitial(self, invitation):
        if "invitation_to_task_interstitial" not in self.project.root_task.module.spec:
            return None
        return {
            "body":
                self.project.root_task.render_field("invitation_to_task_interstitial",
                    invitation=invitation,
                    task=self,
                ),
            "continue_text": "Start " + self.title,
            "alt_url": self.project.get_absolute_url(),
            "alt_text": "Learn more about " + self.project.title,
        }

    # MISC

    def get_open_invitations(self, user, org):
        # Return the open Invitations for transferring task ownership
        # elsewhere, sent from the user.
        from siteapp.models import Invitation
        invs = Invitation.get_for(self).filter(organization=org, from_user=user)
        for inv in invs:
            inv.from_user.localize_to_org(org)
        return invs

    def get_source_invitation(self, user, org):
        inv = self.invitation_history.filter(accepted_user=user).order_by('-created').first()
        if inv:
            inv.from_user.localize_to_org(org)
        return inv

    # NOTIFICATION TARGET HELEPRS

    def get_notification_watchers(self):
        return self.project.get_members()

    def render_title(self):
        # Project root tasks derive their rendered title from the
        # project title and don't use the instance-name.
        if self == self.project.root_task:
            return self.project.title
        return self.render_simple_string("instance-name", self.module.title)

    def render_invitation_message(self):
        return self.render_simple_string("invitation-message",
            'Can you take over answering %s for %s and let me know when it is done?'
                % (self.title, self.project.title))

    def render_simple_string(self, field, default):
        try:
            return render_content(
                {
                    "template": self.module.spec[field],
                    "format": "text",
                },
                self.get_answers().with_extended_info(), # get answers + imputed answers
                "text",
                "%s %s" % (repr(self.module), field)
            )
        except (KeyError, ValueError):
            return default

    def render_field(self, field, **additional_context):
        return render_content(
            self.module.spec.get(field) or "",
            ModuleAnswers(self.module, self, {}),
            "html",
            "%s %s" % (repr(self.module), field),
            additional_context=additional_context
        )

    def render_output_documents(self, answers=None):
        if answers is None:
            answers = self.get_answers()
        return answers.render_output({})

    def render_snippet(self):
        snippet = self.module.spec.get("snippet")
        if not snippet: return None
        return render_content(
            snippet,
            self.get_answers().with_extended_info(), # get answers + imputed answers
            "html",
            "%s snippet" % repr(self.module)
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
            # we're creating and appending a new task.

            # Which module will the Task instantiate?
            module = q.answer_type_module
            if module is None:
                raise ValueError("The question specifies a protocol -- it can't be answered this way.")

            # Create the Task.
            task = Task.create(
                parent_task_answer=ans, # for instrumentation only, doesn't go into Task instance
                project=self.project,
                editor=user,
                module=module,
                title=module.title)

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

            # Clear the cached data.
            self.cached_is_finished = None
            self.save(update_fields=["cached_is_finished"])

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

    def export_json(self, serializer):
        # Exports this Task's current answers to a JSON-serializable Python data structure.
        # The export is recurisve --- all answers to sub-modules are included, and so on.
        # Called via siteapp.Project::export_json. No authorization is performed within here
        # so the caller should have administrative access. Especially since the export may
        # include not just this Task's answers but also the answers of sub-tasks.

        # Since a Task can be used many times throughout a project as the answer
        # to different module and module-set questions, we use serializeOnce to
        # assign the Task a unique ID in the output and then if it's attempted to
        # be serialized again, serializeOnce just outputs a reference to the ID
        # and doesn't call the lambda function below.
        from collections import OrderedDict
        return serializer.serializeOnce(
            self,
            "task:" + str(self.uuid), # used to create a unique key if the Task is attempted to be serialzied more than once
            lambda : OrderedDict([ # "lambda :" makes this able to be evaluated lazily
                ("id", str(self.uuid)), # a uuid.UUID instance is JSON-serializable but let's just make it a string so there are no surprises
                ("title", self.title),
                ("created", self.created.isoformat()),
                ("modified", self.updated.isoformat()),
                ("module", self.module.export_json(serializer)),
                ("answers", OrderedDict([
                    (q.question.key, q.export_json(serializer))
                    for q in self.answers.all().order_by("question__definition_order")
                    ])),
            ])
            )

    @staticmethod
    def import_json(data, deserializer, for_question):
        def do_deserialize():
            # Gets or creates a Task instance corresponding to the Task encoded
            # in the data. The Task must be an answer to a TaskQuestion instance,
            # given as for_question, which determines the Module that the task
            # uses.

            # Basic validation.
            if not isinstance(data, dict):
                deserializer.log("Data format error.")
                return
            if not isinstance(data.get("id"), str):
                deserializer.log("Data format error.")
                return

            # If there's a Task in the system with the UUID found in the incoming
            # data, use that, assuming the user has write permission on it and it
            # is a part of the same organization as the question it answers.
            task = Task.objects.filter(uuid=data["id"], project__organization=for_question.task.project.organization).first()
            if task:
                if not task.has_write_priv(deserializer.user):
                    deserializer.log("%s (%s): You do not have permission to update that task."
                        % (task.title, data['id']))
                    return None

            else:
                # The UUID doesn't correspond with anything in the database, so
                # create a new task.
                task = Task.create(
                    parent_task_answer=for_question, # for instrumentation only, doesn't go into Task instance
                    editor=deserializer.user,
                    project=for_question.task.project,
                    module=for_question.question.answer_type_module,
                    title=for_question.question.answer_type_module.title,
                    uuid=data['id'], # preserve the UUID from the incoming data
                    )

            # Recursively fill in the answers to the newly created task.
            task.import_json_update(data, deserializer)
            return task

        # If the serialized data is a reference to something we've already deserialized
        # and imported, then return the Task directly. Otherwise call do_deserialize to
        # do the actual work of deserializing & updating a Task.
        return deserializer.deserializeOnce(data, do_deserialize)

    def import_json_update(self, data, deserializer):
        # Imports/overwrites/merges question answers from the given data structure
        # into this Task, and into any sub-Tasks that are answers to questions.
        # The user is known only to have write permission to this Task.

        # Since this method is called directly on a Project root task, we must
        # repeat some of the same validation that occurs in Task.import_json.
        if not isinstance(data, dict):
            deserializer.log("Data format error.")
            return

        # Overwrite metadata if the fields are present, i.e. allow for
        # missing or empty fields, which will preserve the existing metadata we have.
        self.title = data.get("title") or self.title
        self.save(update_fields=["title"])

        # We don't chek that the module listed in the data matches the module
        # this Task actually uses in the database. We don't have a way to test
        # equality and if there's a mismatch there's nothing we can really do.
        # Instead we just carefully validate the incoming answers.

        my_name = "%s (%s)" % (self.title, data.get("id") or "no UUID")
        did_update_any_questions = False

        # Merge answers to questions.

        if "answers" in data:
            if not isinstance(data["answers"], dict):
                deserializer.log("Data format error.")
                return

            # Loop through the key-value pairs.
            for qkey, answer in data["answers"].items():
                # Get the ModuleQuestion instance for this question.
                q = self.module.questions.filter(key=qkey).first()
                if q is None:
                    deserializer.log("Task %s question %s ignored (not a valid question ID)." % (my_name, qkey))
                    continue

                # For logging.
                qname = q.spec.get("title") or qkey

                # Ensure the data type matches the current question specification.
                if answer and q.spec["type"] != answer.get("questionType"):
                    deserializer.log("Task %s question %s ignored (question type mismatch)." % (my_name, qname))
                    continue

                # Validate the answer value (check data type, range), if it is answered.
                # (Any question can be skipped.)
                if answer and answer.get("value") is not None:
                    try:
                        value = validator.validate(q, answer["value"])
                    except ValueError as e:
                        deserializer.log("Task %s question %s ignored: %s" % (my_name, qname, str(e)))
                        continue
                else:
                    # The value is None so we don't validate. Any question
                    # can be answered with None, meaning it was skipped.
                    value = None

                # Get or create the TaskAnswer instance for this question.
                taskanswer, _ = TaskAnswer.objects.get_or_create(
                    task=self,
                    question=q,
                )

                if answer is None:
                    # A null answer means the question has no answer - it's cleared.
                    # (A "skipped" question has an answer whose value is null.)
                    taskanswer.clear_answer(deserializer.user)
                    continue

                # Prepare the fields for saving.
                prep_fields = TaskAnswerHistory.import_json_prep(taskanswer, value, deserializer)
                if prep_fields is None:
                    deserializer.log("Task %s question %s has been skipped because a sub-task could not be used." % (my_name, qname))
                    continue

                value, answered_by_tasks, answered_by_file = prep_fields

                # And save the answer.
                if taskanswer.save_answer(value, answered_by_tasks, answered_by_file, deserializer.user):
                    deserializer.log("Task %s question %s was updated." % (my_name, qname))
                    did_update_any_questions = True
                
            if not did_update_any_questions:
                deserializer.log("Task %s had no new answers to save." % (my_name,))


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
        return self.task.get_absolute_url_to_question(self.question)

    def get_current_answer(self):
        # The current answer is the one with the highest primary key.
        return self.answer_history.order_by('-id').first()

    def has_answer(self):
        ans = self.get_current_answer()
        if ans and not ans.cleared:
            return True
        return False

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
            elif answer.is_skipped():
                vp = "skipped the question"
                is_cleared = False
            elif is_cleared:
                if self.question.spec["type"] == "interstitial":
                    # answer doesn't make sense here
                    vp = "acknowledged this page"
                else:
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
                "user": who,
                "user_is_in_text": True,
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

    def clear_answer(self, user):
        ans = self.get_current_answer()
        if ans is None or ans.cleared:
            # No answer record yet or the record has already marked the question
            # as cleared.
            return False

        # Store a new TaskAnswerHistory record with the cleared flag set.
        TaskAnswerHistory.objects.create(
            taskanswer=self,
            answered_by=user,
            stored_value=None,
            answered_by_file=None,
            cleared=True)

        # kick the Task and TaskAnswer's updated field
        self.task.save(update_fields=[])
        self.save(update_fields=[])
        return True

    def save_answer(self, value, answered_by_tasks, answered_by_file, user, encryption_provider=None):
        # Apply any encoding/encryption.

        value_encoding = None

        if self.question.spec.get("encrypt") == "emphemeral-user-key" and value is not None:
            # Encrypt the value before it goes into the database (except
            # the null value --- don't encrypt whether or not the question
            # was skipped).

            if encryption_provider is None:
                raise ValueError("Cannot save an answer to this question because encryption is required but is not available in this context.")

            # Use an encryption key that is held by the user (not by Q)
            # and expires on its own short timeframe. Each ephemerally
            # encrypted value gets a different encryption key so that
            # each value can expire on its own timeframe.
            import json
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            key_id, lifetime = encryption_provider.set_new_ephemeral_user_key(key)
            value_encoding = {
                "method": "encrypted-emphemeral-user-key",
                "version": 0,
                "key_id": key_id,
                "lifetime": lifetime, # in seconds
            }
            value = Fernet(key)\
                .encrypt(json.dumps(value).encode("utf8"))\
                .decode("ascii")

        # Save the answer and return True if the answer was changed (vs was not
        # updated because the value matched the value of the existing answer).
        current_answer = self.get_current_answer()

        # Check if the answer is changing. If not, return False.

        def read_file(f):
            f.open()
            try:
                return f.read()
            finally:
                f.close()

        def are_files_same():
            if answered_by_file is None and current_answer.answered_by_file.name == "":
                # No files in either case -- so the file field is the same.
                return True
            if answered_by_file is None or current_answer.answered_by_file.name == "":
                # One but not both are null, so there is a change.
                return False
            # Both have content -- check if the content matches.
            return read_file(answered_by_file) == current_answer.answered_by_file.read()

        if current_answer and not current_answer.cleared \
            and value == current_answer.stored_value \
            and value_encoding == current_answer.stored_encoding \
            and set(answered_by_tasks) == set(current_answer.answered_by_task.all()) \
            and are_files_same():
            return False

        # The answer is new or changing. Create a new record for it.
        answer = TaskAnswerHistory.objects.create(
            taskanswer=self,
            answered_by=user,
            stored_value=value,
            stored_encoding=value_encoding,
            answered_by_file=answered_by_file)
        for t in answered_by_tasks:
            answer.answered_by_task.add(t)

        # kick the Task and TaskAnswer's updated field, and clear the Task's
        # cache_is_finished field.
        self.task.cached_is_finished = None
        self.task.save(update_fields=["cached_is_finished"])
        self.save(update_fields=[])

        # Return True to indicate we saved something.
        return True

    # required to attach a Discussion to it
    @property
    def title(self):
        return self.question.spec["title"] + " - " + self.task.title

    # required to attach a Discussion to it
    def is_discussion_deleted(self):
        return self.task.deleted_at

    # required to attach a Discussion to it
    def get_discussion_participants(self):
        return User.objects.filter(projectmembership__project=self.task.project).distinct()

    # required to attach a Discussion to it
    def get_project_context_dict(self):
        return {
            "id": self.task.project.id,
            "title": self.task.project.title,
        }

    # required to attach a Discussion to it
    def get_discussion_interleaved_events(self, events_since):
        return [
            event
            for event in self.get_history()
            if event["date_posix"] > float(events_since)
        ]

    # required to attach a Discussion to it
    def get_user_role(self, user):
        if user == self.task.editor:
            return "editor"
        mbr = ProjectMembership.objects.filter(
            project=self.task.project,
            user=user).first()
        if mbr:
            if mbr.is_admin:
                return "team admin"
            else:
                return "project member"
        return None

    # required to attach a Discussion to it
    def can_invite_guests(self, user):
        return ProjectMembership.objects.filter(project=self.task.project, user=user).exists()

    # required to attach a Discussion to it
    def get_notification_watchers(self):
        return list(mbr.user for mbr in ProjectMembership.objects.filter(project=self.task.project))

    # required to attach a Discussion to it
    def get_discussion_autocompletes(self, organization):
        return {
            # @-mention other participants in the discussion
            "@": [
                {
                    "user_id": user.id,
                    "tag": user.username,
                    "display": user.render_context_dict(organization)["name"],
                }
                for user in self.get_discussion_participants()
            ],

            # #-mention Organization-defined terms
            "#": [
                {
                    "tag": term,
                }
                for term in organization.extra.get("vocabulary", [])
            ]
        }



    def export_json(self, serializer):
        # Exports this TaskAnswer's current answer to a JSON-serializable Python data structure.
        # Called via siteapp.Project::export_json.
        ans = self.get_current_answer()
        if ans is None or ans.cleared:
            # There is no current answer.
            return None
        # Call the TaskAnswerHistory serialiation function.
        return ans.export_json(serializer)

class TaskAnswerHistory(models.Model):
    taskanswer = models.ForeignKey(TaskAnswer, related_name="answer_history", on_delete=models.CASCADE, help_text="The TaskAnswer that this is an aswer to.")

    answered_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user that provided this answer.")

    stored_value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")
    stored_encoding = JSONField(blank=True, null=True, default=None, help_text="If not null, this field describes how stored_value is encoded and/or encrypted.")

    answered_by_task = models.ManyToManyField(Task, blank=True, related_name="is_answer_to", help_text="A Task or Tasks that supplies the answer for this question (of type 'module' or 'module-set').")
    answered_by_file = models.FileField(upload_to='q/files', blank=True, null=True)

    cleared = models.BooleanField(default=False, help_text="Set to True to indicate that the user wants to clear their answer. This is different from a null-valued answer, which means not applicable/don't know/skip.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this TaskAnswerHistory.")

    thumbnail = models.FileField(upload_to='q/thumbnails', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class CantDecrypt(Exception):
        pass

    def __repr__(self):
        # For debugging.
        return "<TaskAnswerHistory %s>" % (repr(self.taskanswer),)

    def is_latest(self):
        # Is this the most recent --- the current --- answer for a TaskAnswer.
        return self.taskanswer.get_current_answer() == self

    def is_skipped(self):
        # A skipped question is one whose answer is None,
        # except for interstitial questions where a None
        # indicates they've seen the question.
        if self.taskanswer.question.spec['type'] == "interstitial": return False
        try:
            if self.get_value(raise_if_cant_decrypt=True) is None:
                return True
        except TaskAnswerHistory.CantDecrypt:
            # If we have an answer but we can't decrypt it, it's not skipped.
            return False

    def get_value(self, decryption_provider=None, raise_if_cant_decrypt=False):
        if self.cleared:
            raise RuntimeError("get_value cannot be called on a cleared answer")

        # Get the ModuleQuestion that defines the type of the question
        # that this answer is for.
        q = self.taskanswer.question

        # If this question type is "module" or "module-set", its answer
        # is stored in the answered_by_task M2M field and the stored_value
        # field is not used. The return value is an uninitialized ModuleAnswers
        # instance, an array of instances, that will lazy-load the answers
        # when needed.
        if q.spec["type"] in ("module", "module-set"):
            value = [
                ModuleAnswers(t.module, t, None)
                for t in self.answered_by_task.all().select_related('module')
                ]
            if q.spec["type"] == "module":
                if len(value) == 0:
                    # The question is skipped.
                    return None
                else:
                    # The question is answered - it has just one answer.
                    return value[0]
            elif q.spec["type"] == "module-set":
                # Return the array of answers.
                return value

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
            sf = StoredFile.objects.only("mime_type").get(path=blob.name)
            return {
                "url": settings.SITE_ROOT_URL + blob.url,
                "size": blob.size,
                "type": sf.mime_type,
            }
        
        # For all other question types, the value is stored in the stored_value
        # field.
        else:
            if self.stored_encoding is None:
                # The value is stored as JSON.
                return self.stored_value

            elif isinstance(self.stored_encoding, dict):

                if self.stored_encoding.get('method') == "encrypted-emphemeral-user-key":
                    if decryption_provider is not None:
                        # Get the encryption key and decrypt the value.
                        # See save_answer.
                        import json
                        from cryptography.fernet import Fernet
                        try:
                            key = decryption_provider.get_ephemeral_user_key(self.stored_encoding.get('key_id'))
                            fernet = Fernet(key)
                            return json.loads(
                                fernet.decrypt(self.stored_value.encode("ascii"))
                                .decode("ascii")
                                )
                        except (TypeError, ValueError):
                            # Encryption key was not valid.
                            pass

                    # We could not decrypt.
                    if raise_if_cant_decrypt:
                        raise TaskAnswerHistory.CantDecrypt()
                    else:
                        # Treat this answer as if it were skipped.
                        return None

                else:
                    raise Exception("Invalid method in stored_encoding field.")

            else:
                raise Exception("Invalid value in stored_encoding field.")

    def get_answer_display(self):
        if self.cleared:
            return "[marked unanswered]"
        if self.taskanswer.question.spec["type"] in ("module", "module-set"):
            return repr(self.answered_by_task.all())
        else:
            try:
                return repr(self.get_value(raise_if_cant_decrypt=True))
            except TaskAnswerHistory.CantDecrypt:
                return "[encrypted]"

    def export_json(self, serializer):
        # Exports this TaskAnswerHistory's value to a JSON-serializable Python data structure.
        # Called via siteapp.Project::export_json.
        #
        # The data structure should match the output format of module_logic.question_input_parser
        # and the input format expected by module_logic.validator.validate() because the
        # validate function is called during import.

        # Get the answer's current value.
        value = self.get_value()
        q = self.taskanswer.question

        # If it's not a skipped value, we may need further processing.
        if value is not None:
            if q.spec["type"] == "module":
                # It's a ModuleAnswers instance -- serialize the Task itself.
                value = value.task.export_json(serializer)
            
            elif q.spec["type"] == "module-set":
                # It's an array of ModuleAnswers instances.
                value = [x.task.export_json(serializer) for x in value]
            
            elif q.spec["type"] == "file":
                # Although self.get_value() returns useful data, it's not the export
                # format because it doesn't include the file content (only a URL to it).
                # Add the file content to it. It's other important field is 'type' which
                # holds the MIME type.
                import re
                from base64 import b64encode
                value.update({
                    "content": re.findall(".{1,64}", b64encode(self.answered_by_file.read()).decode("ascii")),
                })

            else:
                # Any value that we might have stored in the database is definitely
                # JSON-serializabile because that's how it's stored. Special question
                # types like "file" should be sure to only generate JSON-serializable
                # content, or else we need to update this.
                pass

        from collections import OrderedDict
        return OrderedDict([
            ("questionType", q.spec["type"]), # so that deserialization can interpret the value
            ("answeredBy", str(self.answered_by)),
            ("answeredAt", self.created.isoformat()),
            ("value", value),
        ])

    @staticmethod
    def import_json_prep(taskanswer, value, deserializer):
        # Given a JSON-serializable data structure produced by export_json, prepare
        # it for saving as a new answer by returning content for our stored_value,
        # answered_by_tasks, and answered_by_file database fields.

        answered_by_tasks = set()
        answered_by_file = None

        # Skipped questions.
        if value is None:
            return value, answered_by_tasks, answered_by_file

        # Special question types that aren't stored in the stored_value field.
        q = taskanswer.question
        if q.spec["type"] in ("module", "module-set"):
            # These questions are stored

            # Make module-type questions look like module-set questions
            # so we can handle the rest the same.
            if q.spec["type"] == "module":
                value = [value]

            # For each sub-taks, get or create the Task instance (and
            # recurse to update its answers). Task.import_json can return
            # None, and we handle that below.
            for task in value:
                task = Task.import_json(task, deserializer, taskanswer)
                answered_by_tasks.add(task)

            # Skip updating this question if there was any error fetching
            # a Task.
            if None in answered_by_tasks:
                # Could not import.
                return None

            # Reset this part.
            value = None

        elif q.spec["type"] == "file":
            # The value is a Django ContentFile and is stored in a dedicated field
            answered_by_file = value
            value = None

        return value, answered_by_tasks, answered_by_file


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
