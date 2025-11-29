from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DoctorProfile
from django.contrib.auth import get_user_model

#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
#def create_doctor_profile(sender, instance, created, **kwargs):
 #   if created and hasattr(instance, "is_doctor") and instance.is_doctor:
  #      DoctorProfile.objects.create(user=instance, specialization="General")

User = get_user_model()

@receiver(post_save, sender=User)
def create_doctor_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Only create profile if user is in Doctor group
    if instance.groups.filter(name="Doctor").exists():
        DoctorProfile.objects.get_or_create(
            user=instance,
            defaults={"specialization": "General"}
        )
