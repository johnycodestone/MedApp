from celery import shared_task
from django.core.mail import send_mail
from .models import Appointment

@shared_task
def send_appointment_reminder(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        subject = "Appointment Reminder"
        message = f"Dear {appointment.patient.username}, you have an appointment with Dr. {appointment.doctor.username} at {appointment.scheduled_time}."
        send_mail(subject, message, 'noreply@medapp.com', [appointment.patient.email])
    except Appointment.DoesNotExist:
        pass
