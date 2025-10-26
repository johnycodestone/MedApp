# reports/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Report, ReportCategory

# -------------------------------
# Signal: Validate Report before saving
# -------------------------------
@receiver(pre_save, sender=Report)
def validate_report_before_save(sender, instance, **kwargs):
    """
    Ensure report timestamps are valid before saving.
    - published_at must be after generated_at
    - If status is PUBLISHED and no published_at is set, assign it automatically
    """
    if instance.published_at and instance.generated_at:
        if instance.published_at < instance.generated_at:
            raise ValueError("Published time must be after generation time")

    if instance.status == Report.ReportStatus.PUBLISHED and not instance.published_at:
        instance.published_at = timezone.now()

# -------------------------------
# Signal: Update category stats after report save
# -------------------------------
@receiver(post_save, sender=Report)
def update_report_category_stats(sender, instance, created, **kwargs):
    """
    Placeholder for updating category-level statistics after report save.
    Extend this to track counts, averages, etc.
    """
    if instance.category:
        # Example: increment report count, update last_updated, etc.
        pass

# -------------------------------
# Signal: Validate ReportCategory before saving
# -------------------------------
@receiver(pre_save, sender=ReportCategory)
def validate_report_category(sender, instance, **kwargs):
    """
    Ensure category names are unique (case-insensitive).
    """
    existing_categories = ReportCategory.objects.filter(
        name__iexact=instance.name
    ).exclude(pk=instance.pk)

    if existing_categories.exists():
        raise ValueError("A category with this name already exists.")

# -------------------------------
# Post-migrate hook: Seed default report categories
# -------------------------------
def populate_report_categories(sender, **kwargs):
    """
    Safely seed default report categories after migrations.
    This avoids premature DB access during app initialization.
    """
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
        },
        {
            'name': 'Research Reports',
            'description': 'Academic and clinical research reports',
            'report_type': 'RESEARCH'
        }
    ]

    with transaction.atomic():
        for category_data in default_categories:
            ReportCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
