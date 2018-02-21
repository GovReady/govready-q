from django.db import models, transaction
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

from collections import OrderedDict
import uuid

from .module_logic import ModuleAnswers, render_content
from .answer_validation import validator
from siteapp.models import User, Organization, Project, ProjectMembership

class AppSource(models.Model):
    is_system_source = models.BooleanField(default=False, help_text="This field is set to True for a single AppSource that holds the system modules such as user profiles.")
    slug = models.CharField(max_length=200, unique=True, help_text="A unique URL-safe string that names this AppSource.")
    spec = JSONField(help_text="A load_modules ModuleRepository spec.", load_kwargs={'object_pairs_hook': OrderedDict})

    trust_assets = models.BooleanField(default=False, help_text="Are assets trusted? Assets include Javascript that will be served on our domain, Python code included with Modules, and Jinja2 templates in Modules.")
    available_to_all = models.BooleanField(default=True, help_text="Turn off to restrict the Modules loaded from this source to particular organizations.")
    available_to_orgs = models.ManyToManyField(Organization, blank=True, help_text="If available_to_all is False, list the Organizations that can start projects defined by Modules provided by this AppSource.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __str__(self):
        # for the admin
        return self.slug

    def get_description(self):
        if self.spec["type"] == "null":
            return "null source"
        if self.spec["type"] == "local":
            return "local filesystem at %s" % self.spec.get("path")
        if self.spec["type"] == "git":
            return self.spec.get("url")
        if self.spec["type"] == "github":
            return "github.com/%s" % self.spec.get("repo")

    def make_cache_stale_key(self):
        import hashlib, json
        h = hashlib.sha1()
        h.update(json.dumps(self.spec).encode("utf8"))
        h.update(self.updated.isoformat().encode("ascii"))
        return h.hexdigest()

    def open(self):
        # Return an AppSourceConnection instance for this source.
        from .module_sources import AppSourceConnection
        return AppSourceConnection.create(self)

class AppInstance(models.Model):
    source = models.ForeignKey(AppSource, related_name="appinstances", on_delete=models.CASCADE, help_text="The source of this AppInstance.")
    appname = models.CharField(max_length=200, db_index=True, help_text="The name of the app in the AppSource.")

        # the field below is a NullBooleanField because the unique constraint doesn't kick in
        # for NULLs but does for False/True, and we want the constraint to apply only for True.
    system_app = models.NullBooleanField(default=None, help_text="Set to True for AppInstances that are the current version of a system app that provides system-expected Modules. A constraint ensures that only one (source, name) pair can be true.")

    class Meta:
        unique_together = [
            ("source", "appname", "system_app")
        ]

    def __str__(self):
        # For the admin.
        return "%s [%d] (from %s)" % (self.appname, self.id, self.source)

    def __repr__(self):
        # For debugging.
        return "<AppInstance [%d] %s from %s>" % (self.id, self.appname, self.source)


class Module(models.Model):
    source = models.ForeignKey(AppSource, related_name="modules", on_delete=models.CASCADE, help_text="The source of this module definition.")
    app = models.ForeignKey(AppInstance, null=True, related_name="modules", on_delete=models.CASCADE, help_text="The AppInstance that this Module is a part of. Null for legacy Modules created before we had this field.")

    module_name = models.SlugField(max_length=200, help_text="A slug-like identifier for the Module that is unique within the AppInstance app.")

    superseded_by = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, help_text="This field is no longer used. When a Module is superseded by a new version, this points to the newer version.")

    spec = JSONField(help_text="Module definition data.", load_kwargs={'object_pairs_hook': OrderedDict})
    assets = models.ForeignKey('ModuleAssetPack', blank=True, null=True, on_delete=models.CASCADE, help_text="A mapping from asset paths to ModuleAsset instances with the binary content of the asset.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [
            ("app", "module_name"),
        ]

    def __str__(self):
        # For the admin.
        return "%s %s [%d]" % (self.app, self.module_name, self.id)

    def __repr__(self):
        # For debugging.
        return "<Module [%d] %s %s (%s)>" % (self.id, self.module_name, self.spec.get("title", "<No Title>")[0:30], self.app)

    def save(self):
        if self.source != self.app.source: raise ValueError("Module source != app.source.")
        super(Module, self).save()

    @property
    def title(self):
        return self.spec["title"]

    def spec_yaml(self):
        import rtyaml
        return rtyaml.dump(self.spec)

    def get_questions(self):
        # Return the ModuleQuestions in definition order.
        return list(self.questions.order_by('definition_order'))

    def export_json(self, serializer):
        # Exports this Module's metadata to a JSON-serializable Python data structure.
        # Called via siteapp.Project::export_json.
        from collections import OrderedDict
        return serializer.serializeOnce(
            self,
            "module:" + self.app.source.slug + "/" + self.app.appname + "/" + self.module_name, # a preferred key, doesn't need to be unique here
            lambda : OrderedDict([  # "lambda :" makes this able to be evaluated lazily
                ("key", self.module_name),
                ("created", self.created.isoformat()),
                ("modified", self.updated.isoformat()),
        ]))

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

    def is_authoring_tool_enabled(self, user):
        return (
                self.app is not None # legacy Module not associated with an AppInstance
            and self.source.spec["type"] == "local" # so we can save to disk
            and user.has_perm('guidedmodules.change_module'))
    def get_referenceable_modules(self):
        # Return the modules that can be referenced by this
        # one in YAML as an answer type. That's any Module
        # defined in the same AppInstance that isn't "type: project".
        if self.app is None: return # legacy Module not associated with an AppInstance
        for m in self.app.modules.all():
            if m.spec.get("type") == "project": continue
            yield m
    def getReferenceTo(self, target):
        # Get the string that you would put in a YAML file to reference the
        # target module. target must be in get_referenceable_modules.
        # This is the inverse of validate_module_specification.resolve_relative_module_id.
        if self.app != target.app:
            raise ValueError("Cannot reference %s from %s." % (target, self))
        return target.module_name
    def serialize_to_disk(self):
        # Write out the in-memory module specification to disk!
        assert self.source.spec["type"] == "local" and self.source.spec["path"]
        import os.path
        import rtyaml
        spec = OrderedDict(self.spec)
        spec["questions"] = []
        for i, q in enumerate(self.questions.order_by('definition_order')):
            if i == 0 and q.key == "_introduction":
                spec["introduction"] = { "format": "markdown", "template": q.spec["prompt"] }
                continue

            # Rewrite some fields that get rewritten during module-loading.
            qspec = OrderedDict(q.spec)
            if q.answer_type_module:
                qspec["module-id"] = self.getReferenceTo(q.answer_type_module)

            spec["questions"].append(qspec)
        fn = os.path.join(self.source.spec["path"], self.app.appname, self.module_name + ".yaml")
        with open(fn, "w") as f:
            f.write(rtyaml.dump(spec))


class ModuleAsset(models.Model):
    source = models.ForeignKey(AppSource, on_delete=models.CASCADE, help_text="The source of the asset.")
    content_hash = models.CharField(max_length=64, help_text="A hash of the asset binary content, as provided by the source.")
    file = models.FileField(upload_to='guidedmodules/module-assets', help_text="The attached file.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('source', 'content_hash')]

class ModuleAssetPack(models.Model):
    source = models.ForeignKey(AppSource, on_delete=models.CASCADE, help_text="The source of these assets.")
    assets = models.ManyToManyField(ModuleAsset, help_text="The assets linked to this pack.")
    basepath = models.SlugField(max_length=100, help_text="The base path of all assets in this pack.")
    paths = JSONField(help_text="A dictionary mapping file paths to the content_hashes of assets included in the assets field of this instance.")
    total_hash = models.CharField(max_length=64, help_text="A SHA256 hash over the paths and the content_hashes of the assets.")

    trust_assets = models.BooleanField(default=False, help_text="Are assets trusted? Assets include Javascript that will be served on our domain, Python code included with Modules, and Jinja2 templates in Modules.")

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
                    "trust_assets": self.source.trust_assets,
                    "basepath": self.basepath,
                    "paths": self.paths,
                },
                sort_keys=True,
            ).encode("utf8")
        )
        self.total_hash = m.hexdigest()

    def get(self, asset_path):
        if asset_path not in self.paths:
            raise ValueError(asset_path + " is not an asset.")
        return self.assets.get(content_hash=self.paths[asset_path]).file


class ModuleQuestion(models.Model):
    module = models.ForeignKey(Module, related_name="questions", on_delete=models.CASCADE, help_text="The Module that this ModuleQuestion is a part of.")
    key = models.SlugField(max_length=100, help_text="A slug-like identifier for the question.")

    definition_order = models.IntegerField(help_text="An integer giving the order in which this question is defined by the Module.")
    spec = JSONField(help_text="Module definition data.", load_kwargs={'object_pairs_hook': OrderedDict})
    answer_type_module = models.ForeignKey(Module, blank=True, null=True, related_name="is_type_of_answer_to", on_delete=models.PROTECT, help_text="For module and module-set typed questions, this is the Module that Tasks that answer this question must be for.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [("module", "key")]

    def __str__(self):
        # For the admin.
        return "%s[%d].%s" % (self.module, self.module.id, self.key)

    def __repr__(self):
        # For debugging.
        return "<ModuleQuestion [%d] %s.%s (%s)>" % (self.id, self.module.module_name, self.key, repr(self.module))

    def choices_as_csv(self):
        # Helper method for module authoring.
        import csv, io
        buf = io.StringIO()
        wr = csv.writer(buf, delimiter="|")
        for choice in self.spec.get("choices", []):
            wr.writerow([ choice.get("key") or "", choice.get("text") or "", choice.get("help") or "" ])
        return buf.getvalue()

    @staticmethod
    def choices_from_csv(choices):
        # Helper method for module authoring.
        import csv, io, collections
        ret = []
        buf = io.StringIO(choices)
        for choice in csv.reader(buf, delimiter="|"):
            ch = collections.OrderedDict()
            ch["key"] = choice[0]
            if len(choice) >= 2 and choice[1]: ch["text"] = choice[1]
            if len(choice) >= 3 and choice[2]: ch["help"] = choice[2]
            ret.append(ch)
        return ret

    def value_explanation(self):
        # Explain for the authoring tool what a valid value is for this question.
        if self.spec["type"] == "interstitial":
            return "Always null."
        if self.spec["type"] in ("text", "password", "email-address", "url"):
            return "A text string."
        if self.spec["type"] == "date":
            return "A text string in the format 'YYYY-MM-DD'."
        if self.spec["type"] == "longtext":
            return "A text string in CommonMark syntax."
        if self.spec["type"] in ("integer", "real"):
            return "A number."
        if self.spec["type"] == "yesno":
            return '"yes" or "no"'
        if self.spec["type"] == "choice":
            import json
            return "One of " + ", ".join(json.dumps(choice['key']) for choice in self.spec["choices"]) + "."
        if self.spec["type"] == "multiple-choice":
            import json
            return "An array containing " + ", ".join(json.dumps(choice['key']) for choice in self.spec["choices"]) + "."
        return ""

class Task(models.Model):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE, help_text="The Project that this Task is a part of, or empty for Tasks that are just directly owned by the user.")
    editor = models.ForeignKey(User, related_name="tasks_editor_of", on_delete=models.PROTECT, help_text="The user that has primary responsibility for completing this Task.")
    module = models.ForeignKey(Module, on_delete=models.PROTECT, help_text="The Module that this Task is answering.")

    title_override = models.CharField(max_length=256, blank=True, null=True, help_text="The title of this Task if overriding the computed instance-name or Module.title default.")
    notes = models.TextField(blank=True, help_text="Notes set by the user about why they are completing this task.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True, help_text="If 'deleted' by a user, the date & time the Task was deleted.")

    cached_state = JSONField(blank=True, default=None, help_text="Cached value storing whether the Task is finished, its computed title, and other state that depends on question answers.")

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
        # don't use title because it's expensive and might cause recursion
        # issues since the URL to this task might be generated when rendering the title.
        from django.utils.text import slugify
        return slugify(self.module.spec['title'])

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

    def get_static_asset_url(self, asset_path, use_data_urls=False):
        if not self.module.assets or asset_path not in self.module.assets.paths:
            # No assets are defined for this Module, or this path is not
            # an asset, so just return the path as it's probably an absolute URL.
            return asset_path
        if not use_data_urls:
            return self.get_absolute_url() + "/media/" + asset_path
        else:
            return self.get_static_asset_image_data_url(asset_path, 640)

    def get_static_asset_image_data_url(self, asset_path, max_image_size):
        if not self.module.assets or asset_path not in self.module.assets.paths:
            # No assets are defined for this Module, or this path is not
            # an asset.
            raise ValueError(asset_path + " is not an asset.")
        with self.module.assets.get(asset_path) as f:
            try:
                return image_to_dataurl(f, max_image_size)
            except:
                # image processing error
                raise ValueError(asset_path + " has invalid image data.")


    # ANSWERS

    def get_current_answer_records(self):
        # Efficiently get the current answer to every question.
        #
        # Since we track the history of answers to each question, we need to get the most
        # recent answer for each question. It's fastest if we pre-load the complete history
        # of every question rather than making a separate database call for each question
        # to find its most recent answer. See TaskAnswer.get_current_answer().
        answers = list(
            TaskAnswerHistory.objects
                .filter(taskanswer__task=self)
                .order_by('-id')
                .select_related('taskanswer', 'taskanswer__task', 'taskanswer__question', 'answered_by')
                .prefetch_related('answered_by_task')
                .prefetch_related("answered_by_task__module__app__source")
                .prefetch_related("answered_by_task__module__questions")
                )
        def get_current_answer(q):
            for a in answers:
                if a.taskanswer.question == q:
                    return a
            return None

        # Loop over all of the questions and fetch each's answer.
        for q in sorted(self.module.questions.all(), key = lambda q : q.definition_order):
            # Get the latest TaskAnswerHistory instance for this TaskAnswer,
            # if there is any (there should be). If the answer is marked as
            # cleared, then treat as if it had not been answered.
            a = get_current_answer(q) # faster than but equivalent to q.get_current_answer()
            if a and a.cleared: a = None
            yield (q, a)

    def get_answers(self):
        # Return a ModuleAnswers instance that wraps this Task and its Pythonic answer values.
        # The dict of answers is ordered to preserve the question definition order.
        answertuples = OrderedDict()
        for q, a in self.get_current_answer_records():
            # Get the value of that answer.
            if a is not None:
                is_answered = True
                value = a.get_value()
            else:
                is_answered = False
                value = None
            answertuples[q.key] = (q, is_answered, a, value)
        return ModuleAnswers(self.module, self, answertuples)

    def get_last_modification(self):
        ans = TaskAnswerHistory.objects\
                .filter(taskanswer__task=self)\
                .order_by('-id')\
                .first()
        return ans

    # STATE

    def can_transfer_owner(self):
        return not self.project.is_account_project

    def is_started(self):
        return self.answers.exists()

    def is_finished(self):
        # Check that all questions that need an answer have
        # an answer and that all module-type questions are
        # finished.
        if self.cached_state is None:
            self.cached_state = { }
        if "is_finished" not in self.cached_state:
            self.cached_state["is_finished"] = self.is_finished_uncached()
            self.save(update_fields=["cached_state"])
        return self.cached_state["is_finished"]

    def is_finished_uncached(self):
        # Check that all questions that need an answer have
        # an answer and that all module-type questions are
        # finished.
        try:
            answers = self.get_answers().with_extended_info(required=True)
        except Exception:
            # If there is an error evaluating imputed conditions,
            # just say the task is unfinished.
            return False
        if len(answers.can_answer) != 0:
            return False
        for a in answers.as_dict().values():
            # module-type questions
            if isinstance(a, ModuleAnswers) and a.task:
                if not a.task.is_finished():
                    return False
            # module-set-type questions
            if isinstance(a, list):
                for item in a:
                    if isinstance(item, ModuleAnswers) and item.task:
                        if not item.task.is_finished():
                            return False
        return True

    def get_progress_percent(self):
        if self.cached_state is None:
            self.cached_state = { }
        if "progress_percent" not in self.cached_state:
            answered, total = self.compute_progress_percent()
            self.cached_state["progress_percent"] = (answered/total*100) if (total > 0) else 100
            self.save(update_fields=["cached_state"])
        return self.cached_state["progress_percent"]

    def compute_progress_percent(self):
        # Return a tuple of the number of questions that have an answer
        # and the total number of questions. For module-type questions
        # that are answered, recursively add the questions of the inner module.
        try:
            answers = self.get_answers().with_extended_info()
        except Exception:
            # If there is an error evaluating imputed conditions,
            # just say the task is empty.
            return (0, 0)

        num_answered = 0
        num_questions = 0
        for (q, is_answered, a, value) in answers.answertuples.values():
            # module-type questions with a real answer
            if isinstance(value, ModuleAnswers) and value.task:
                inner_answered, inner_total = value.task.compute_progress_percent()
                num_answered += inner_answered
                num_questions += inner_total

            # all other questions
            else:
                if is_answered:
                    num_answered += 1
                num_questions += 1

        return (num_answered, num_questions)


    # This method is called any time an answer to any of this Task's questions
    # is changed, or for questions that are answered by sub-tasks, and if any
    # of their answers changed too, recursively.
    #
    # * Clear the Task's cache_is_finished field.
    # * Recursively call on_answer_changed on any Tasks that this task is
    #   a current answer of a question to.
    def on_answer_changed(self, seen_tasks=None):
        if seen_tasks is None: seen_tasks = set()
        if self in seen_tasks: return
        seen_tasks.add(self)
        self.cached_state = None
        self.save(update_fields=["cached_state", "updated"])
        for ans in self.is_answer_to.select_related('taskanswer__task').all():
            if ans.is_latest():
                ans.taskanswer.task.on_answer_changed(seen_tasks)

    def get_status_display(self):
        # Is this task done?
        if not self.is_finished():
            return "In Progress, last edit " + self.updated.strftime("%x %X")
        else:
            return "Finished on " + self.updated.strftime("%x %X")

    # AUTHZ

    @staticmethod
    def get_all_tasks_readable_by(user, org, recursive=False):
        # Symmetric with get_access_level == "READ". See that for the basic logic.
        tasks = Task.objects.filter(
            models.Q(editor=user) | models.Q(project__members__user=user),
            project__organization=org,
            deleted_at=None,
            ).distinct()

        if recursive:
            # Add in all tasks that these tasks refer to via answers to questions.
            # (Including tasks in the same project because those may reference
            # other tasks in other projects with different access levels.)
            seen_task_ids = set(t.id for t in tasks)
            tasks1 = tasks
            while len(tasks1) > 0:
                # Collect all of the tasks referenced by the last batch as answers,
                # except ones we've already seen.
                tasks2 = set()
                for t in tasks1:
                    for q, a in t.get_current_answer_records():
                        if a:
                            tasks2 |= set(a.answered_by_task.all())
                tasks2_ids = set(tt.id for tt in tasks2)
                seen_task_ids |= tasks2_ids
                tasks |= Task.objects.filter(id__in=tasks2_ids).distinct()
                tasks1 = tasks2

        return tasks

    def get_access_level(self, user, allow_access_to_deleted=False, recursive=True):
        # symmetric with get_all_tasks_readable_by
        if self.deleted_at and not allow_access_to_deleted:
            return False
        if self.editor == user:
            # The editor.
            return "WRITE"
        if ProjectMembership.objects.filter(project=self.project, user=user).exists():
            # All project members have read-write access to the tasks in that projectget.
            return "WRITE"

        if recursive:
            # Access also comes from access to any Task that refers to this Task as a
            # *current* answer to the question. First fetch all tasks that refer to this
            # task, and then filter to see if the answer is current. Include Tasks in
            # the same project because they may in turn be answers to tasks in other
            # projects. Expand this out recursively.
            parent_tasks = set()
            search_tasks = [self]
            while len(search_tasks) > 0:
                ptasks = set(
                    tah.taskanswer.task
                    for tah in TaskAnswerHistory.objects
                        .filter(answered_by_task__in=search_tasks)
                        .exclude(taskanswer__task__id__in=[t.id for t in parent_tasks])
                        .select_related("taskanswer__task"))
                parent_tasks |= ptasks
                search_tasks = ptasks

            access_levels = set(t.get_access_level(user, recursive=False) for t in parent_tasks)
            if "WRITE" in access_levels:
                return "WRITE"
            if "READ" in access_levels:
                return "READ"

        return None

    def has_read_priv(self, user, allow_access_to_deleted=False):
        return self.get_access_level(user, allow_access_to_deleted=allow_access_to_deleted) in ("READ", "WRITE")

    def has_write_priv(self, user, allow_access_to_deleted=False):
        return self.get_access_level(user, allow_access_to_deleted=allow_access_to_deleted) == "WRITE"

    def has_review_priv(self, user):
        return user in self.project.organization.reviewers.all()


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

    # COMPUTED PROPERTIES

    IS_COMPUTING_TITLE = False

    @property
    def title(self):
        # If the title_override is set, return that.
        # Otherwise, if the Module has an instance-name field, render that template.
        # Last, fall back to the Module title.
        if self.title_override:
            return self.title_override

        if "instance-name" not in self.module.spec:
            return self.module.spec["title"]

        # Render the instance-name template if its rendered value is not cached.
        if self.cached_state is None:
            self.cached_state = { }
        if "title" not in self.cached_state:

            if Task.IS_COMPUTING_TITLE:
                # Hopefully this never occurs, but rendering the instance-name
                # template could end up causing the task's title to be computed.
                raise RuntimeError("Infinite recursion!")

            Task.IS_COMPUTING_TITLE = True
            try:
                title = self.render_simple_string(
                    "instance-name", self.module.spec["title"],
                    is_computing_title=True).strip()
            finally:
                Task.IS_COMPUTING_TITLE = False

            self.cached_state["title"] = title
            self.save(update_fields=["cached_state"])

        return self.cached_state["title"]


    def render_introduction(self):
        # Project tasks have an introduction field.
        return self.render_field("introduction")

    def render_invitation_message(self):
        return self.render_simple_string("invitation-message",
            'Can you take over answering %s for %s and let me know when it is done?'
                % (self.title, self.project.title))

    def render_simple_string(self, field, default, **kwargs):
        try:
            return render_content(
                {
                    "template": self.module.spec[field],
                    "format": "text",
                },
                self.get_answers().with_extended_info(), # get answers + imputed answers
                "text",
                "%s %s" % (repr(self.module), field),
                **kwargs
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

    def render_output_documents(self, answers=None, use_data_urls=False):
        if answers is None:
            answers = self.get_answers()
        return answers.render_output({}, use_data_urls=use_data_urls)

    def render_snippet(self):
        snippet = self.module.spec.get("snippet")
        if not snippet: return None
        return render_content(
            snippet,
            self.get_answers().with_extended_info(), # get answers + imputed answers
            "html",
            "%s snippet" % repr(self.module)
        )


    def get_app_icon_url(self):
        icon_img = self.module.spec.get("icon")
        if icon_img:
            try:
                return self.get_static_asset_image_data_url(icon_img, 75)
            except ValueError:
                # no asset or image error
                pass
        return None

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
        if not isinstance(question_id, ModuleQuestion):
            q = self.module.questions.get(key=question_id)
        else:
            q = question_id

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
                module=module)

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

            # Mark that the Task has had an answer changed.
            self.on_answer_changed()

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
        # The export is recursive --- all answers to sub-modules are included, and so on.
        # Called via siteapp.Project::export_json. No authorization is performed within here
        # so the caller should have administrative access. Especially since the export may
        # include not just this Task's answers but also the answers of sub-tasks.

        # Since a Task can be used many times throughout a project as the answer
        # to different module and module-set questions, we use serializeOnce to
        # assign the Task a unique ID in the output and then if it's attempted to
        # be serialized again, serializeOnce just outputs a reference to the ID
        # and doesn't call the lambda function below.

        from collections import OrderedDict

        def build_dict():
            if serializer.include_metadata:
                return OrderedDict([
                    ("id", str(self.uuid)), # a uuid.UUID instance is JSON-serializable but let's just make it a string so there are no surprises
                    ("title", self.title),
                    ("created", self.created.isoformat()),
                    ("modified", self.updated.isoformat()),
                    ("module", self.module.export_json(serializer)),
                    ("answers", build_answers()),
                ])
            else:
                return build_answers()

        def build_answers():
            # Create a dict holding the user-entered and imputed answers to
            # questions in this task.
            ret = OrderedDict()
            answers = self.get_answers().with_extended_info()
            for q, a in self.get_current_answer_records():
                if q.key in answers.was_imputed:
                    # This was imputed. Ignore any user answer and serialize
                    # with a dummy TaskAnswerHistory.
                    a = TaskAnswerHistory(taskanswer=TaskAnswer(question=q), stored_value=answers.as_dict()[q.key])
                elif a is None:
                    continue
                elif not serializer.include_metadata and q.spec["type"] == "interstitial":
                    # If we're not including metadata, there's no reason to
                    # include interstitials in output because their value is
                    # always null.
                    continue
                a.export_json(ret, serializer)
            return ret

        return serializer.serializeOnce(
            self,
            "task:" + str(self.uuid), # used to create a unique key if the Task is attempted to be serialzied more than once
            build_dict)

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

        if deserializer.included_metadata:
            # Overwrite metadata if the fields are present, i.e. allow for
            # missing or empty fields, which will preserve the existing metadata we have.
            # Only update the title if what's stored in the serialized data doesn't
            # match the automatically computed title.
            if data.get("title") and data["title"] != self.title:
                self.title_override = data["title"]
                self.save(update_fields=["title_override"])

        # We don't chek that the module listed in the data matches the module
        # this Task actually uses in the database. We don't have a way to test
        # equality and if there's a mismatch there's nothing we can really do.
        # Instead we just carefully validate the incoming answers.

        my_name = "%s (%s)" % (self.title, data.get("id") or "no UUID")
        did_update_any_questions = False

        # Merge answers to questions.
        if deserializer.included_metadata:
            data = data.get("answers", {})
        if not isinstance(data, dict):
            deserializer.log("Data format error.")
            return

        # Loop through the key-value pairs.
        for qkey, answer in data.items():
            # Get the ModuleQuestion instance for this question.
            q = self.module.questions.filter(key=qkey).first()
            if q is None:
                deserializer.log("Task %s question %s ignored (not a valid question ID)." % (my_name, qkey))
                continue

            # For logging.
            qname = q.spec.get("title") or qkey

            if deserializer.included_metadata:
                # Skip exported values of imputed questions. We must not write values
                # for questions that are imputed. In the short format where we don't
                # have this metadata, ideally we would not write imputed values back
                # to the database but we can't know if it's imputed unless we run
                # the impute conditions after each question update, which is expensive,
                # so we'll just write the value to the database - but it will be ignored
                # because when retreiving the value it will be overridden by the
                # imputed value.
                if answer and answer.get("imputed") is True:
                    continue

                # Ensure the data type matches the current question specification.
                if answer and q.spec["type"] != answer.get("questionType"):
                    deserializer.log("Task %s question %s ignored (question type mismatch)." % (my_name, qname))
                    continue

                if answer is None or "value" not in answer:
                    has_value = False
                else:
                    has_value = True
                    value = answer["value"]

            else:
                # In the short format, answer is the value itself.
                has_value = True
                value = answer

            # Validate the answer value (check data type, range), if it is answered.
            # (Any question can be skipped.)
            if has_value and value is not None:
                try:
                    value = validator.validate(q, value)
                except ValueError as e:
                    deserializer.log("Task %s question %s ignored: %s" % (my_name, qname, str(e)))
                    continue

            # Get or create the TaskAnswer instance for this question.
            taskanswer, _ = TaskAnswer.objects.get_or_create(
                task=self,
                question=q,
            )

            if not has_value:
                # A null answer means the question has no answer - it's cleared.
                # (A "skipped" question has an answer whose value is null.)
                taskanswer.clear_answer(deserializer.user)
                continue

            # Prepare the fields for saving.
            prep_fields = TaskAnswerHistory.import_json_prep(taskanswer, value, deserializer)
            if prep_fields is None:
                deserializer.log("Task %s question %s has been skipped because a sub-task could not be used." % (my_name, qname))
                continue

            value, answered_by_tasks, answered_by_file, subtasks_updated = prep_fields

            # And save the answer.
            if taskanswer.save_answer(value, answered_by_tasks, answered_by_file, deserializer.user, deserializer.answer_method):
                deserializer.log("Task %s question %s was updated." % (my_name, qname))
                did_update_any_questions = True
            elif not subtasks_updated:
                # Warn if a value was not changed.
                deserializer.log("Task %s question %s was not changed." % (my_name, qname))

            # If any sub-task data was updated, don't warn about this task not being updated.
            if subtasks_updated:
                did_update_any_questions = True
            
        if not did_update_any_questions:
            deserializer.log("Task %s had no new answers to save." % (my_name,))

        return did_update_any_questions


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

        # The invitation of the help squad.
        if (self.extra or {}).get("invited-help-squad"):
            history.append({
                "type": "event",
                "date": self.extra["invited-help-squad"],
                "html": html.escape("Help squad invited to this discussion."),
                "notification_text": "Help squad invited to this discussion.",
            })

        # Sort.
        history.sort(key = lambda item : item["date"])

        # render events for easier client-side processing
        from django.utils.dateparse import parse_datetime
        for item in history:
            if isinstance(item["date"], str): item["date"] = parse_datetime(item["date"])
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

        # Kick the TaskAnswer's updated fields and the Task to mark that the
        # answer has changed.
        self.save(update_fields=[])
        self.task.on_answer_changed()
        return True

    def save_answer(self, value, answered_by_tasks, answered_by_file, user, method):
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

        value_encoding = None
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
            answered_by_method=method,
            stored_value=value,
            stored_encoding=value_encoding,
            answered_by_file=answered_by_file)
        for t in answered_by_tasks:
            answer.answered_by_task.add(t)

        # Kick the Task and TaskAnswer's updated field and let the Task know that
        # its answers have changed.
        self.save(update_fields=[])
        self.task.on_answer_changed()

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

    # required to attach a Discussion to it
    def on_discussion_comment(self, comment):
        # A comment was left. If we haven't already, invite all organization
        # help crew members to this discussion. See siteapp.views.send_invitation
        # for how to construct Invitations.
        from siteapp.models import Invitation
        self.extra = self.extra or { } # ensure initialized
        if not self.extra.get("invited-help-squad"):
            anyone_invited = False
            for user in self.task.project.organization.help_squad.all():
                if user in self.get_notification_watchers(): continue # no need to invite
                inv = Invitation.objects.create(
                    organization=self.task.project.organization,
                    from_user=comment.user,
                    from_project=self.task.project,
                    target=comment.discussion,
                    target_info={ "what": "invite-guest" },
                    to_user=user,
                    text="The organization's help squad is being automatically invited to help with the following comment:\n\n" + comment.text,
                )
                inv.send()
                anyone_invited = True
            if anyone_invited:
                self.extra["invited-help-squad"] = timezone.now()
                self.save()


class TaskAnswerHistory(models.Model):
    taskanswer = models.ForeignKey(TaskAnswer, related_name="answer_history", on_delete=models.CASCADE, help_text="The TaskAnswer that this is an aswer to.")

    answered_by = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user that provided this answer.")
    answered_by_method = models.CharField(max_length=3, choices=[("web", "Web"), ("imp", "Import"), ("api", "API")], help_text="How this answer was submitted, via the website by a user, via the Export/Import mechanism, or via an API programmatically.")

    stored_value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")
    stored_encoding = JSONField(blank=True, null=True, default=None, help_text="If not null, this field describes how stored_value is encoded and/or encrypted.")

    answered_by_task = models.ManyToManyField(Task, blank=True, related_name="is_answer_to", help_text="A Task or Tasks that supplies the answer for this question (of type 'module' or 'module-set').")
    answered_by_file = models.FileField(upload_to='q/files', blank=True, null=True)

    cleared = models.BooleanField(default=False, help_text="Set to True to indicate that the user wants to clear their answer. This is different from a null-valued answer, which means not applicable/don't know/skip.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this TaskAnswerHistory.")

    REVIEW_CHOICES = [(0, 'Not Reviewed'), (1, 'Reviewed'), (2, 'Approved')]
    reviewed = models.IntegerField(default=0, choices=REVIEW_CHOICES, help_text="Whether this answer has been reviewed and/or approved. All new answers begin with zero. Positive values represent review steps in the organization's workflow.")

    thumbnail = models.FileField(upload_to='q/thumbnails', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        verbose_name_plural = "TaskAnswerHistories"

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
        return (self.get_value() is None)

    def get_value(self):
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
                for t in self.answered_by_task.all()
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

            # Create a display string explaining the file type.
            if sf.mime_type == "text/plain":
                file_type = "plain text"
            elif sf.mime_type.startswith("image/"):
                file_type = "image"
            elif sf.mime_type == "text/html":
                file_type = "HTML"
            else:
                import mimetypes
                file_type = mimetypes.guess_extension(sf.mime_type, strict=False)[1:]

            # Get the URL that can retreive the resource. It's behind
            # auth so we don't use blob.url, which won't work because
            # we haven't exposed that url route.
            import urllib
            url = self.taskanswer.task.get_absolute_url() \
                + "/question/" + urllib.parse.quote(self.taskanswer.question.key) \
                + "/history/" + str(self.id) \
                + "/media"

            # Make it an absolute URL so that when we expose it through
            # the API it makes sense.
            url = self.taskanswer.task.project.organization.get_url(url)

            # Convert it to a data URL so that it can be rendered in exported documents.
            content_dataurl = None
            if q.spec.get("file-type") == "image":
                content_dataurl = image_to_dataurl(self.answered_by_file, 640)

            # Construct a thumbnail and a URL to it.
            thumbnail_url = None
            thumbnail_dataurl = None
            if not self.thumbnail:
                # Try to construct a thumbnail.
                if sf.mime_type == "text/html":
                    # Use wkhtmltoimage.
                    import subprocess
                    try:
                        # Pipe to subprocess.
                        # xvfb is required to run wkhtmltopdf in headless mode on Debian, see https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2037#issuecomment-62019521.
                        cmd = ["xvfb-run", "--", "wkhtmltoimage",
                                "-q", # else errors go to stdout
                                "--disable-javascript",
                                "-f", "png",
                                # "--disable-smart-width", - generates a warning on stdout that qt is unpatched, which happens in headless mode
                                "--zoom", ".7",
                                "--width", "700",
                                "--height", str(int(700*9/16)),
                                "-", "-"]
                        with subprocess.Popen(cmd,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            ) as proc:
                            stdout, stderr = proc.communicate(
                                self.answered_by_file.read(),
                                timeout=10)
                            if proc.returncode != 0: raise subprocess.CalledProcessError(proc.returncode, ' '.join(cmd))

                        # Store PNG.
                        from django.core.files.base import ContentFile
                        value = ContentFile(stdout)
                        value.name = "thumbnail.png" # needs a name for the storage backend?
                        self.thumbnail = value
                        self.save(update_fields=["thumbnail"])
                    except subprocess.CalledProcessError as e:
                        print(e)

            if self.thumbnail:
                # If we have a thumbnail, indicate so by returning a URL to it.
                thumbnail_url = url + "?thumbnail=1"
                thumbnail_dataurl = image_to_dataurl(self.thumbnail, 640)

            return {
                "url": url,
                "content_dataurl": content_dataurl,
                "size": blob.size,
                "type": sf.mime_type,
                "type_display": file_type,
                "thumbnail_url": thumbnail_url,
                "thumbnail_dataurl": thumbnail_dataurl,
            }
        
        # For all other question types, the value is stored in the stored_value
        # field.
        else:
            if self.stored_encoding is None:
                # The value is stored as JSON.
                return self.stored_value

            elif isinstance(self.stored_encoding, dict):

                if self.stored_encoding.get('method') == "encrypted-emphemeral-user-key":
                    # This was an old ephemeral encrpytion method that is no longer
                    # supported. Keys are certainly gone by now anyway. Treat this
                    # question as if it were skipped.
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
            return repr(self.get_value())

    def export_json(self, parent_dict, serializer):
        # Exports this TaskAnswerHistory's value to a JSON-serializable Python data structure.
        # Called via siteapp.Project::export_json.
        #
        # The data structure should match the output format of answer_validation.question_input_parser
        # and the input format expected by answer_validation.validator.validate() because the
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
                if serializer.include_file_content:
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

        # Get a human-readable form to include in the output.
        human_readable_text = None
        if value is not None:
            if q.spec["type"] == "longtext":
                # Longtext is Markdown. Turn into HTML.
                from CommonMarkExtensions.tables import \
                    ParserWithTables as CommonMarkParser, \
                    RendererWithTables as CommonMarkHtmlRenderer
                human_readable_text_key = "html"
                human_readable_text = CommonMarkHtmlRenderer().render(CommonMarkParser().parse(value)).strip()

            elif q.spec["type"] in ("choice", "multiple-choice"):
                # Get the 'text' values for the choices.
                human_readable_text_key = "text"
                choices = { c["key"]: c["text"] for c in q.spec["choices"] }
                if q.spec["type"] == "choice":
                    human_readable_text = choices.get(value)
                elif q.spec["type"] == "multiple-choice":
                    human_readable_text = [choices.get(v) for v in value]

            elif q.spec["type"] == "yesno":
                human_readable_text_key = "text"
                human_readable_text = "Yes" if (value == "yes") else "No"

        if not serializer.include_metadata:
            # Just return the value.
            parent_dict[q.key] = value
            if human_readable_text is not None:
                parent_dict[q.key + "." + human_readable_text_key] = human_readable_text

        else:
            # The export should also include metadata about the answer, like
            # who answered it and when.
            from collections import OrderedDict
            ret = OrderedDict()
            if self.id:
                ret["answeredBy"] = str(self.answered_by)
                ret["answeredAt"] = self.created.isoformat()
                ret["answeredByMethod"] = str(self.answered_by_method)
            else:
                ret["imputed"] = True
            ret["questionType"] = q.spec["type"] # so that deserialization can validate the value
            ret["value"] = value
            if human_readable_text is not None:
                ret[human_readable_text_key] = human_readable_text
            parent_dict[q.key] = ret

    @staticmethod
    def import_json_prep(taskanswer, value, deserializer):
        # Given a JSON-serializable data structure produced by export_json, prepare
        # it for saving as a new answer by returning content for our stored_value,
        # answered_by_tasks, and answered_by_file database fields.

        answered_by_tasks = set()
        answered_by_file = None
        subtasks_updated = False

        # Skipped questions.
        if value is None:
            return value, answered_by_tasks, answered_by_file, subtasks_updated

        # Special question types that aren't stored in the stored_value field.
        q = taskanswer.question
        if q.spec["type"] in ("module", "module-set"):
            # These questions are stored in the answered_by_tasks field
            # as foreign keys to other Task instances.

            if deserializer.included_metadata:
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
                    subtasks_updated = True # TODO: Should be False if task existed and no change made.

                # Skip updating this question if there was any error fetching
                # a Task.
                if None in answered_by_tasks:
                    # Could not import.
                    return None

            else:
                # In the short form, the inner tasks are serialized as dicts
                # of answers. No UUIDs are stored to data with existing tasks,
                # so module-set questions would be difficult to update. For
                # module questions, we can create the sub-Task if it hasn't
                # been started or update the existing one. We can return None
                # to signal that this question cannot be updated.
                if q.spec["type"] != "module": return None
                try:
                    t = Task.get_or_create_subtask(taskanswer.task, deserializer.user, taskanswer.question.key, create=True)
                except ValueError:
                    # Can't create sub-Task because question specifies a
                    # protocol and not a module.
                    return None

                # This is redundant. The answer has already been updated by
                # get_or_create_subtask.
                answered_by_tasks.add(t)

                # Import data in the sub-Task.
                subtasks_updated = t.import_json_update(value, deserializer)

            # Reset this variable so stored_value is set to None.
            value = None

        elif q.spec["type"] == "file":
            # The value is a Django ContentFile and is stored in a dedicated field
            answered_by_file = value
            value = None

        return value, answered_by_tasks, answered_by_file, subtasks_updated


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

def image_to_dataurl(f, size):
    from PIL import Image
    from io import BytesIO
    import base64
    if isinstance(f, Image.Image):
        # If a PIL.Image is passed in, then use it.
        im = f.copy()
    else:
        # Either a bytes stream (e.g. BytesIO) or a bytes string are passed in.
        # If a string, convert to a stream. Then load using PIL.Image.open.
        if isinstance(f, bytes):
            f = BytesIO(f)
        im = Image.open(f)
    im.thumbnail((size, size))
    buf = BytesIO()
    im.save(buf, "png")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
