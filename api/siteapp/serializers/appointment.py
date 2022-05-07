from api.base.serializers.types import ReadOnlySerializer, WriteOnlySerializer
from siteapp.models import Appointment


class SimpleAppointmentSerializer(ReadOnlySerializer):
    class Meta:
        model = Appointment
        fields = ['role', 'party', 'model_name', 'comment']

class WriteAppointmentSerializer(WriteOnlySerializer):
    class Meta:
        model = Appointment
        fields = ['role', 'party', 'model_name', 'comment']
