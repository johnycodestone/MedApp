from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DoctorProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and hasattr(instance, "is_doctor") and instance.is_doctor:
        DoctorProfile.objects.create(user=instance, specialization="General")
