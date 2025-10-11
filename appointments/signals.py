from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment
from .tasks import send_appointment_reminder

@receiver(post_save, sender=Appointment)
def trigger_reminder(sender, instance, created, **kwargs):
    if created:
        send_appointment_reminder.delay(instance.id)
