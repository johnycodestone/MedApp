from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Hospital

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_hospital_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff and hasattr(instance, "is_hospital"):  # hypothetical flag
        Hospital.objects.create(user=instance, name=f"Hospital {instance.username}")
