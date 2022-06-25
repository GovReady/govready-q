from api.base.serializers.types import ReadOnlySerializer
from api.guidedmodules.serializers.modules import DetailedModuleSerializer, DetailedModuleQuestionSerializer
from api.guidedmodules.serializers.tasks import DetailedTaskSerializer, DetailedTaskAnswerSerializer
from api.siteapp.serializers.projects import DetailedProjectsSerializer
from api.siteapp.serializers.users import SimpleUserSerializer
from guidedmodules.models import InstrumentationEvent


class SimpleInstrumentationEventSerializer(ReadOnlySerializer):
    class Meta:
        model = InstrumentationEvent
        fields = ['event_time', 'event_type', 'event_value', 'extra']


class DetailedInstrumentationEventSerializer(SimpleInstrumentationEventSerializer):
    user = SimpleUserSerializer()
    module = DetailedModuleSerializer()
    question = DetailedModuleQuestionSerializer()
    project = DetailedProjectsSerializer()
    task = DetailedTaskSerializer()
    answer = DetailedTaskAnswerSerializer()

    class Meta:
        model = InstrumentationEvent
        fields = SimpleInstrumentationEventSerializer.Meta.fields + ['user', 'module', 'question', 'project', 'task',
                                                                     'answer']


