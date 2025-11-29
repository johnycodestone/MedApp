from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Appointment, AppointmentStatus
from .tasks import send_appointment_reminder

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Appointment)
def trigger_reminder(sender, instance, created, **kwargs):
    """
    Signal to trigger reminder task when a new appointment is created.
    - Only schedules reminders for pending/confirmed appointments.
    - Skips if appointment is in the past.
    """
    if created:
        if instance.status in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            if instance.scheduled_time > timezone.now():
                send_appointment_reminder.delay(instance.id)
                logger.info(f"Reminder scheduled for appointment {instance.id}")
            else:
                logger.info(f"Skipping reminder: appointment {instance.id} is in the past")
        else:
            logger.info(f"Skipping reminder: appointment {instance.id} has status {instance.status}")
