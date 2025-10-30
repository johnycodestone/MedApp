# adminpanel/signals.py

"""
Signal handlers for adminpanel system models.
Automatically logs and audits changes to configurations, backups, and system logs.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    SystemConfiguration,
    BackupRecord,
    AuditLog
)
from .services import (
    log_system_event,
    record_audit_log
)

# -------------------------------
# SystemConfiguration Change Audit
# -------------------------------
@receiver(post_save, sender=SystemConfiguration)
def audit_config_change(sender, instance, created, **kwargs):
    """
    Records an audit log when a configuration is created or updated.
    """
    action = 'CREATE' if created else 'UPDATE'
    changes = {
        'key': instance.key,
        'value': instance.value,
        'data_type': instance.data_type,
        'category': instance.category,
        'is_active': instance.is_active
    }
    record_audit_log(
        action=action,
        model_name='SystemConfiguration',
        object_id=instance.id,
        object_repr=str(instance),
        user=instance.created_by,
        changes=changes
    )

# -------------------------------
# Backup Completion Logging
# -------------------------------
@receiver(post_save, sender=BackupRecord)
def log_backup_status(sender, instance, created, **kwargs):
    """
    Logs backup completion or failure events.
    """
    if not created and instance.status in ['COMPLETED', 'FAILED']:
        log_system_event(
            level='INFO' if instance.status == 'COMPLETED' else 'ERROR',
            category='BACKUP',
            message=f"Backup {instance.get_backup_type_display()} marked as {instance.get_status_display()}",
            user=instance.initiated_by,
            ip=None,
            path=None,
            metadata={
                'backup_id': instance.id,
                'file_path': instance.file_path,
                'error': instance.error_message
            }
        )

# -------------------------------
# Configuration Deletion Audit
# -------------------------------
@receiver(post_delete, sender=SystemConfiguration)
def audit_config_deletion(sender, instance, **kwargs):
    """
    Records an audit log when a configuration is deleted.
    """
    record_audit_log(
        action='DELETE',
        model_name='SystemConfiguration',
        object_id=instance.id,
        object_repr=str(instance),
        user=instance.created_by,
        changes={'key': instance.key}
    )
