from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prescription

@receiver(post_save, sender=Prescription)
def notify_patient_on_prescription(sender, instance, created, **kwargs):
    if created:
        # Trigger notification or email
        pass
