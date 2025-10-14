from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Report, ReportCategory

@receiver(pre_save, sender=Report)
def validate_report_before_save(sender, instance, **kwargs):
    """
    Validate report before saving
    """
    # Ensure end time is after start time
    if instance.published_at and instance.generated_at:
        if instance.published_at < instance.generated_at:
            raise ValueError("Published time must be after generation time")
    
    # Set published time if status is published
    if instance.status == Report.ReportStatus.PUBLISHED and not instance.published_at:
        instance.published_at = timezone.now()

@receiver(post_save, sender=Report)
def update_report_category_stats(sender, instance, created, **kwargs):
    """
    Update report category statistics after report creation or update
    """
    if instance.category:
        # You can add custom logic here to update category-level statistics
        pass

@receiver(pre_save, sender=ReportCategory)
def validate_report_category(sender, instance, **kwargs):
    """
    Validate report category before saving
    """
    # Ensure unique category names (case-insensitive)
    existing_categories = ReportCategory.objects.filter(
        name__iexact=instance.name
    ).exclude(pk=instance.pk)
    
    if existing_categories.exists():
        raise ValueError("A category with this name already exists.")

def validate_report_configurations():
    """
    Validate and set up initial report configurations
    """
    # Create default report categories if they don't exist
    default_categories = [
        {
            'name': 'Medical Reports', 
            'description': 'Standard medical reports',
            'report_type': 'MEDICAL'
        },
        {
            'name': 'Financial Reports', 
            'description': 'Financial and billing reports',
            'report_type': 'FINANCIAL'
        },
        {
            'name': 'Operational Reports', 
            'description': 'Hospital operational reports',
            'report_type': 'OPERATIONAL'
        }
    ]
    
    for category_data in default_categories:
        ReportCategory.objects.get_or_create(
            name=category_data['name'], 
            defaults=category_data
        )
