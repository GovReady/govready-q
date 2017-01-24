from django.contrib import admin

from .models import \
	Module, ModuleQuestion, \
	Task, TaskAnswer, TaskAnswerHistory, \
	InstrumentationEvent

class ModuleAdmin(admin.ModelAdmin):
	list_display = ('id', 'key', 'visible', 'superseded_by', 'created')
	raw_id_fields = ('superseded_by',)

class ModuleQuestionAdmin(admin.ModelAdmin):
	raw_id_fields = ('module', 'answer_type_module')

class TaskAdmin(admin.ModelAdmin):
	list_display = ('title', 'organization_and_project', 'editor', 'module', 'is_finished', 'submodule_of', 'created')
	raw_id_fields = ('project', 'editor', 'module')
	readonly_fields = ('module', 'invitation_history')
	def submodule_of(self, obj):
		return obj.is_answer_to_unique()
	def organization_and_project(self, obj):
		return obj.project.organization_and_title()

class TaskAnswerAdmin(admin.ModelAdmin):
	list_display = ('question', 'task', '_project', 'created')
	raw_id_fields = ('task',)
	readonly_fields = ('task', 'question')
	fieldsets = [(None, { "fields": ('task', 'question') }),
	             (None, { "fields": ('notes',) }),
	             (None, { "fields": ('extra',) }), ]
	def _project(self, obj): return obj.task.project

class TaskAnswerHistoryAdmin(admin.ModelAdmin):
	list_display = ('created', 'taskanswer', 'answer', 'answered_by', 'is_latest')
	raw_id_fields = ('taskanswer', 'answered_by', 'answered_by_task')
	readonly_fields = ('taskanswer', 'answered_by', 'created')
	fieldsets = [(None, { "fields": ('created', 'taskanswer', 'answered_by') }),
	             (None, { "fields": ('stored_value', 'stored_encoding', 'cleared') }),
	             (None, { "fields": ('extra',) }) ]
	def answer(self, obj): return obj.get_answer_display()

class InstrumentationEventAdmin(admin.ModelAdmin):
	list_display = ('event_time', 'event_type', 'user', 'event_value', 'task')
	raw_id_fields = ('user', 'module', 'question', 'task', 'answer')
	readonly_fields = ('event_time', 'event_type', 'event_value', 'user', 'module', 'question', 'task', 'answer')

admin.site.register(Module, ModuleAdmin)
admin.site.register(ModuleQuestion, ModuleQuestionAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAnswer, TaskAnswerAdmin)
admin.site.register(TaskAnswerHistory, TaskAnswerHistoryAdmin)
admin.site.register(InstrumentationEvent, InstrumentationEventAdmin)
