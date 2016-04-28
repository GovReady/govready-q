from django.db import models
from django.contrib.auth.models import User

from jsonfield import JSONField

class Task(models.Model):
    user = models.ForeignKey(User, help_text="The user that is working on this task.")
    module_id = models.CharField(max_length=128, help_text="The ID of the module being completed.")

    title = models.CharField(max_length=256, help_text="The title of this Task. If the user is performing multiple tasks for the same module, this title would distiguish the tasks.")
    notes = models.TextField(blank=True, help_text="Notes set by the user about why they are completing this task.")

    requested_by = models.ForeignKey('guidedmodules.Answer', blank=True, null=True, related_name='requesting_tasks', help_text="The Answer that this sub-Task is trying to answer, if applicable.")
    requestor_notes = models.TextField(blank=True, help_text="A message from the requesting user to the user of this Task.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('user', 'module_id'),
        ]

    @staticmethod
    def has_completed_task(user, module_id):
        task = Task.objects.filter(user=user, module_id="account_settings").first()
        if task is None:
            return False
        return task.is_finished()

    @staticmethod
    def get_task_for_module(user, module_id):
        # Gets a task given a module_id. Use only with system modules
        # where a user can only have one Task for the module.
        task, isnew = Task.objects.get_or_create(
            user=user,
            module_id=module_id)
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

    def get_answers_dict(self):
        answered = { }
        for q in self.answer_set.all():
            answered[q.question_id] = q.value
        return answered

    def is_finished(self):
        return self.load_module().next_question(self.get_answers_dict()) == None

    def get_status_display(self):
        if not self.is_finished():
            return "In Progress, last edit " + self.updated.strftime("%x %X")
        else:
            return "FInished on " + self.updated.strftime("%x %X")

    def get_output(self):
        return self.load_module().render_output(self.get_answers_dict())

class Answer(models.Model):
    task = models.ForeignKey(Task, help_text="The Task that this Answer is for.")
    question_id = models.CharField(max_length=128, help_text="The ID of the question (with the Task's module) that this Answer answers.")

    value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this Answer.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('task', 'question_id')]

class Comment(models.Model):
    user = models.ForeignKey(User, help_text="The user making a comment.")
    target = models.ForeignKey(Answer, help_text="The Answer that this comment is attached to.")

    emoji = models.CharField(max_length=64, blank=True, null=True, help_text="The name of an emoji that the user is reacting with.")
    text = models.TextField(blank=True, help_text="The text of the user's comment.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('user', 'target'),
        ]
