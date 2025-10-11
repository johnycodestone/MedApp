from .models import Appointment
from django.utils import timezone

class AppointmentRepository:
    @staticmethod
    def create(patient, doctor, scheduled_time, reason=None):
        return Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduled_time=scheduled_time,
            reason=reason
        )

    @staticmethod
    def get_by_id(appointment_id):
        try:
            return Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return None

    @staticmethod
    def get_upcoming(user):
        return Appointment.objects.filter(
            patient=user,
            scheduled_time__gte=timezone.now()
        ).order_by('scheduled_time')
