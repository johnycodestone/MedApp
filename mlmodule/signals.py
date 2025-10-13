# mlmodule/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prediction

@receiver(post_save, sender=Prediction)
def notify_prediction_created(sender, instance, created, **kwargs):
    if created:
        print(f"New prediction created for patient {instance.patient_id}")
