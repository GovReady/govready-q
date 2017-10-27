from django.contrib import admin
from django import forms
from django.utils.html import escape as escape_html

from .models import \
	AppSource, AppInstance, Module, ModuleQuestion, ModuleAssetPack, ModuleAsset, \
	Task, TaskAnswer, TaskAnswerHistory, \
	InstrumentationEvent

class AppSourceSpecWidget(forms.Widget):
    fields = [
		("type",
		 "Source Type",
		 forms.Select(choices=[
		 	("local", "Local Directory"),
		 	("git", "Git Repository over SSH"),
		 	("github", "Github Repository using Github API")]),
		 "What kind of app source is it?",
		 None),
		("url",
		 "URL",
		 forms.TextInput(),
		 "The URL to the git repository, usually in the format of git@github.com:orgname/reponame.",
		 { "git" }),
		("repo",
		 "Repository",
		 forms.TextInput(),
		 "The repository name in 'organization/repository' format.",
		 { "github" }),
		("branch",
		 "Branch",
		 forms.TextInput(),
		 "The name of the branch in the repository to read apps from.",
		 { "git" }),
		("path",
		 "Path",
		 forms.TextInput(),
		 "The path to the apps. For local directory AppSources, the local directory path. Otherwise the path within the repository, or blank if the apps are at the repository root.",
		 { "local", "git", "github" }),
		("ssh_key",
		 "SSH Key",
		 forms.Textarea(attrs={"rows": 3 }),
		 "If the repository requires an SSH key for access, paste a private key here and send the public key to the repository owner (e.g. as a deploy key on Github and GitLab).",
		 { "git" }),
		("_remaining_",
		 "Other Parameters",
		 forms.Textarea(attrs={"rows": 2 }),
		 "Other parameters specified in YAML.",
		 None),
	]

    def render(self, name, value, attrs=None):
    	# For some reason we get the JSON value as a string.
    	import json, collections
    	value = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(value or "{}")

    	def make_widget(key, label, widget, help_text, show_for_types):
    	    if key != "_remaining_":
    	    	if key in value:
    	    		val = value[key]
    	    		del value[key] # only the unrecognized keys are left at the end
    	    	else:
    	    		val = ""
    	    elif len(value) == 0:
    	    	# Nothing unrecognized.
    	    	val = ""
    	    else:
    	    	# Serialize unrecognized keys in YAML.
    	        import rtyaml
    	        val = rtyaml.dump(value)
    	    return """
    	    	<div style="clear: both; padding-bottom: .75em" class="{}">
    	        	<label for="id_{}_{}">{}:</label>
    	    		{}
    	    		<p class="help">{}</p>
    	    	</div>""".format(
    	    		(
    	    			"show_if_type "
    	    			 + " ".join(("show_if_type_" + s) for s in show_for_types)
    	    			 if show_for_types
    	    			 else ""
    	    		),
		            escape_html(name),
		            key,
		            escape_html(label),
		            widget.render(name + "_" + key, val),
		            escape_html(help_text or ""),
		            )
    	
    	# Widgets
    	ret = "\n\n".join(make_widget(*args) for args in self.fields)

    	# Click handler to only show fields that are appropriate for
    	# the selected AppSource type.
    	ret += """
    	<script>
    		django.jQuery("select[name=spec_type]")
    			.change(function() {
    				django.jQuery(".show_if_type").hide()
    				django.jQuery(".show_if_type_" + this.value).show()
    			})
    			.change() // init
    	</script>
    	"""
    	return ret

    def value_from_datadict(self, data, files, name):
    	# Start with the extra data.
    	import rtyaml, collections
    	value = rtyaml.load(data[name + "__remaining_"]) or collections.OrderedDict()

    	# Add other values.
    	for key, label, widget, help_text, show_for_types in self.fields:
    		val = data.get(name + "_" + key)
    		if val:
    			value[key] = val

    	return value

class AppSourceAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['spec'].widget = AppSourceSpecWidget()
		self.fields['spec'].label = "How is this AppSource accessed?"
		self.fields['spec'].help_text = None

class AppSourceAdmin(admin.ModelAdmin):
	form = AppSourceAdminForm # customize spec widget
	list_display = ('namespace', 'source')
	def source(self, obj):
		return obj.get_description()

class AppInstanceAdmin(admin.ModelAdmin):
	list_display = ('appname', 'source', 'system_app')
	list_filter = ('source', 'system_app')

class ModuleAdmin(admin.ModelAdmin):
	list_display = ('id', 'source', 'app_', 'module_name', 'created')
	list_filter = ('source',)
	raw_id_fields = ('app', 'superseded_by', 'assets')
	def app_(self, obj): return "{} [{}]".format(obj.app.appname, obj.app.id) if obj.app else "(not in an app)"

class ModuleQuestionAdmin(admin.ModelAdmin):
	raw_id_fields = ('module', 'answer_type_module')

class ModuleAssetPackAdmin(admin.ModelAdmin):
	list_display = ('id', 'source', 'basepath', 'created')
	raw_id_fields = ('assets',)
	readonly_fields = ('source','basepath','total_hash','assets','paths','extra')

class ModuleAssetAdmin(admin.ModelAdmin):
	list_display = ('id', 'source', 'content_hash', 'created')
	raw_id_fields = ('source',)
	readonly_fields = ('source','content_hash','file')

class TaskAdmin(admin.ModelAdmin):
	list_display = ('title', 'organization_and_project', 'editor', 'module', 'is_finished', 'submodule_of', 'created')
	raw_id_fields = ('project', 'editor', 'module')
	readonly_fields = ('module', 'invitation_history')
	search_fields = ('title', 'project__title', 'project__organization__name', 'editor__username', 'editor__email', 'module__key')
	def submodule_of(self, obj):
		return obj.is_answer_to_unique()
	def organization_and_project(self, obj):
		return obj.project.organization_and_title()

class TaskAnswerAdmin(admin.ModelAdmin):
	list_display = ('question', 'task', '_project', 'created')
	raw_id_fields = ('task',)
	readonly_fields = ('task', 'question')
	search_fields = ('task__title', 'task__project__title', 'task__project__organization__name', 'task__module__key')
	fieldsets = [(None, { "fields": ('task', 'question') }),
	             (None, { "fields": ('notes',) }),
	             (None, { "fields": ('extra',) }), ]
	def _project(self, obj): return obj.task.project

class TaskAnswerHistoryAdmin(admin.ModelAdmin):
	list_display = ('created', 'taskanswer', 'answered_by', 'is_latest')
	raw_id_fields = ('taskanswer', 'answered_by', 'answered_by_task')
	readonly_fields = ('taskanswer', 'answered_by', 'created')
	search_fields = ('taskanswer__task__title', 'taskanswer__task__project__title', 'taskanswer__task__project__organization__name', 'taskanswer__task__module__key', 'answered_by__username', 'answered_by__email')
	fieldsets = [(None, { "fields": ('created', 'taskanswer', 'answered_by') }),
	             (None, { "fields": ('stored_value', 'stored_encoding', 'cleared') }),
	             (None, { "fields": ('extra',) }) ]
	def answer(self, obj): return obj.get_answer_display()

class InstrumentationEventAdmin(admin.ModelAdmin):
	list_display = ('event_time', 'event_type', 'user', 'event_value', 'task')
	raw_id_fields = ('user', 'module', 'question', 'task', 'answer')
	readonly_fields = ('event_time', 'event_type', 'event_value', 'user', 'module', 'question', 'task', 'answer')

admin.site.register(AppSource, AppSourceAdmin)
admin.site.register(AppInstance, AppInstanceAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ModuleQuestion, ModuleQuestionAdmin)
admin.site.register(ModuleAssetPack, ModuleAssetPackAdmin)
admin.site.register(ModuleAsset, ModuleAssetAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAnswer, TaskAnswerAdmin)
admin.site.register(TaskAnswerHistory, TaskAnswerHistoryAdmin)
admin.site.register(InstrumentationEvent, InstrumentationEventAdmin)
