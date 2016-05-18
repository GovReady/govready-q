from django.contrib import admin

from .models import Task, TaskQuestion, TaskAnswer

class TaskAdmin(admin.ModelAdmin):
	list_display = ('title', 'project', 'editor', '_module', 'is_finished', 'submodule_of', 'created')
	raw_id_fields = ('project', 'editor',)
	readonly_fields = ('module_id', 'invitation_history')
	def _module(self, obj): return obj.load_module().title + " (" + obj.module_id + ")"
	def submodule_of(self, obj):
		ans = obj.is_answer_to_unique()
		if ans:
			return ans.question
		return None

class TaskQuestionAdmin(admin.ModelAdmin):
	list_display = ('_question', '_task', '_project', '_question_id', 'created')
	raw_id_fields = ('task',)
	readonly_fields = ('task', 'question_id')
	fieldsets = [(None, { "fields": ('task', 'question_id') }),
	             (None, { "fields": ('notes',) }),
	             (None, { "fields": ('extra',) }), ]
	def _question(self, obj): return obj.get_question().title
	def _task(self, obj):
		s = obj.task.title
		t = obj.task.load_module().title
		if s != t:
			s += " (" + t + ")"
		return s
	def _project(self, obj): return obj.task.project
	def _module(self, obj): return obj.task.load_module().title
	def _question_id(self, obj): return obj.task.module_id + "." + obj.question_id

class TaskAnswerAdmin(admin.ModelAdmin):
	list_display = ('question', 'answer', 'answered_by', 'is_latest')
	raw_id_fields = ('question', 'answered_by', 'answered_by_task')
	readonly_fields = ('question', 'answered_by')
	fieldsets = [(None, { "fields": ('question', 'answered_by') }),
	             (None, { "fields": ('value', 'answered_by_task') }),
	             (None, { "fields": ('extra',) }) ]
	def answer(self, obj): return obj.get_answer_display()

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskQuestion, TaskQuestionAdmin)
admin.site.register(TaskAnswer, TaskAnswerAdmin)
