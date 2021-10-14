from rest_framework import serializers

from api.base.serializers.types import ReadOnlySerializer
from api.guidedmodules.serializers.modules import DetailedModuleSerializer, DetailedModuleQuestionSerializer, \
    SimpleModuleSerializer
from api.siteapp.serializers.invitations import DetailedInvitationSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from guidedmodules.models import Task, TaskAnswer, TaskAnswerHistory


class SimpleTaskSerializer(ReadOnlySerializer):
    class Meta:
        model = Task
        fields = ['title_override', 'notes', 'deleted_at', 'cached_state', 'extra', 'uuid']

class TaskSerializer(SimpleTaskSerializer):
    module = SimpleModuleSerializer()

    class Meta:
        model = Task
        fields = SimpleTaskSerializer.Meta.fields + [ 'module']


class DetailedTaskSerializer(SimpleTaskSerializer):
    project = serializers.SerializerMethodField()  # Circular Dependency
    editor = SimpleUserSerializer()
    module = DetailedModuleSerializer()
    invitation_history = DetailedInvitationSerializer(many=True)

    def get_project(self, obj):
        from api.siteapp.serializers.projects import DetailedProjectsSerializer
        return DetailedProjectsSerializer(obj)

    class Meta:
        model = Task
        fields = SimpleTaskSerializer.Meta.fields + ['project', 'editor', 'module', 'invitation_history']


class SimpleTaskAnswerSerializer(ReadOnlySerializer):
    class Meta:
        model = TaskAnswer
        fields = ['notes', 'extra']


class DetailedTaskAnswerSerializer(SimpleTaskAnswerSerializer):
    task = DetailedTaskSerializer()
    question = DetailedModuleQuestionSerializer()

    class Meta:
        model = TaskAnswer
        fields = SimpleTaskAnswerSerializer.Meta.fields + ['task', 'question']


class SimpleTaskAnswerHistorySerializer(ReadOnlySerializer):

    class Meta:
        model = TaskAnswerHistory
        fields = ['answered_by_method', 'stored_value', 'stored_encoding', 'answered_by_file', 'skipped_reason',
                  'unsure', 'cleared', 'notes', 'reviewed', 'thumbnail', 'extra']


class DetailedTaskAnswerHistorySerializer(SimpleTaskAnswerHistorySerializer):
    taskanswer = DetailedTaskAnswerSerializer()
    answered_by = SimpleUserSerializer()
    answered_by_task = DetailedTaskSerializer(many=True)

    class Meta:
        model = TaskAnswerHistory
        fields = SimpleTaskAnswerSerializer.Meta.fields + ['taskanswer', 'answered_by', 'answered_by_task', ]
