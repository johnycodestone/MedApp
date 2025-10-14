from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Department

@receiver(post_delete, sender=Department)
def cleanup_after_department_delete(sender, instance, **kwargs):
    # Placeholder for cleanup logic, e.g., notify hospital admin or update related duties.
    pass
