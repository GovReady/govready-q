from api.base.views.base import SerializerClasses
from api.base.views.viewsets import ReadWriteViewSet
from api.siteapp.serializers.appointment import SimpleAppointmentSerializer, WriteAppointmentSerializer
from siteapp.models import Appointment
# from api.siteapp.filters.appointments import AppointmentFilter

class AppointmentViewSet(ReadWriteViewSet):
    queryset = Appointment.objects.all()

    serializer_classes = SerializerClasses(retrieve=SimpleAppointmentSerializer,
                                           list=SimpleAppointmentSerializer,
                                           create=WriteAppointmentSerializer,
                                           update=WriteAppointmentSerializer,
                                           destroy=WriteAppointmentSerializer)
    # filter_class = AppointmentFilter