from django.db import models
from django.http import JsonResponse

class AppointmentModelMixin(models.Model):
    appointments = models.ManyToManyField("siteapp.Appointment", blank=True, related_name="%(class)s")

    class Meta:
        abstract = True

    def add_appointments(self, appointments):
        if appointments is None:
            appointments = []
        elif isinstance(appointments, str):
            appointments = [appointments]
        assert isinstance(appointments, list)
        self.appointments.add(*appointments)

    def remove_appointments(self, appointments=None):
        if appointments is None:
            appointments = []
        elif isinstance(appointments, str):
            appointments = [appointments]
        assert isinstance(appointments, list)
        self.appointments.remove(*appointments)