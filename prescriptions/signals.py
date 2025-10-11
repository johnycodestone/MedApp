# prescriptions/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prescription
from .tasks import generate_pdf_task

@receiver(post_save, sender=Prescription)
def prescription_post_save(sender, instance: Prescription, created, **kwargs):
    """
    When a prescription is saved and its status is finalized, schedule PDF generation.
    If Celery isn't configured in the environment, .delay may raise — that's acceptable;
    it will surface in logs, but will not block the save.
    """
    if instance.status == Prescription.STATUS_FINAL:
        try:
            generate_pdf_task.delay(instance.id)
        except Exception:
            # fail silently for environments without Celery in dev
            pass
