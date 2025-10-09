from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .repositories import get_or_create_profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile_on_user_create(sender, instance, created, **kwargs):
    # Create patient profile automatically when a new user is created.
    if created:
        get_or_create_profile(instance)
