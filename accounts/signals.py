"""
accounts/signals.py

Signal handlers for accounts app.
Handles automatic actions triggered by model events.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create role-specific profile when user is created.
    
    Args:
        sender: Model class (CustomUser)
        instance: User instance
        created: Whether this is a new instance
        **kwargs: Additional arguments
    """
    if created:
        # Import here to avoid circular imports
        if instance.is_hospital():
            from hospitals.models import HospitalProfile
            HospitalProfile.objects.get_or_create(user=instance)
        
        elif instance.is_doctor():
            from doctors.models import DoctorProfile
            DoctorProfile.objects.get_or_create(user=instance)
        
        elif instance.is_patient():
            from patients.models import PatientProfile
            PatientProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=CustomUser)
def log_profile_creation(sender, instance, created, **kwargs):
    """
    Log user profile creation activity.
    
    Args:
        sender: Model class (CustomUser)
        instance: User instance
        created: Whether this is a new instance
        **kwargs: Additional arguments
    """
    if created:
        from .repositories import UserActivityRepository
        
        UserActivityRepository.log_activity(
            user=instance,
            action='REGISTER',
            metadata={
                'role': instance.role,
                'email': instance.email
            }
        )


@receiver(pre_delete, sender=CustomUser)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up user-related data before deletion.
    
    Args:
        sender: Model class (CustomUser)
        instance: User instance being deleted
        **kwargs: Additional arguments
    """
    # Delete verification tokens
    from .models import VerificationToken
    VerificationToken.objects.filter(user=instance).delete()
    
    # Note: UserActivity is handled by CASCADE, but we could archive it first
    # Archive activities before they're deleted
    from .models import UserActivity
    activities = UserActivity.objects.filter(user=instance)
    
    # TODO: Archive activities to a separate table or file before deletion
    # For now, they'll be deleted by CASCADE
    
    # Log the account deletion
    from .repositories import UserActivityRepository
    UserActivityRepository.log_activity(
        user=instance,
        action='PROFILE_UPDATE',
        metadata={'action': 'account_deleted'}
    )


@receiver(post_save, sender=CustomUser)
def send_welcome_email_on_verification(sender, instance, **kwargs):
    """
    Send welcome email when user becomes verified.
    
    Args:
        sender: Model class (CustomUser)
        instance: User instance
        **kwargs: Additional arguments
    """
    # Check if is_verified changed from False to True
    if instance.is_verified and 'is_verified' in kwargs.get('update_fields', []):
        from .tasks import send_welcome_email_task
        
        # Send welcome email asynchronously
        send_welcome_email_task.delay(instance.id)


@receiver(post_save, sender=CustomUser)
def notify_admin_on_new_registration(sender, instance, created, **kwargs):
    """
    Notify administrators about new user registrations.
    
    Args:
        sender: Model class (CustomUser)
        instance: User instance
        created: Whether this is a new instance
        **kwargs: Additional arguments
    """
    if created:
        from django.core.mail import mail_admins
        
        subject = f"New User Registration - {instance.role}"
        message = f"""
        A new user has registered on MedApp:
        
        Username: {instance.username}
        Email: {instance.email}
        Name: {instance.first_name} {instance.last_name}
        Role: {instance.get_role_display()}
        Registration Date: {instance.created_at}
        """
        
        # Send email to admins (async in production)
        try:
            mail_admins(
                subject=subject,
                message=message,
                fail_silently=True
            )
        except Exception:
            # Silently fail to not disrupt user registration
            pass