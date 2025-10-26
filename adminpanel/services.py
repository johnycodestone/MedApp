# adminpanel/services.py

"""
Service layer for adminpanel system operations.
Encapsulates business logic for backups, logs, configurations, and audit trails.
"""

from django.utils import timezone
from django.db import transaction
from .models import (
    BackupRecord,
    SystemLog,
    AuditLog,
    SystemConfiguration
)
from .repositories import (
    get_config_by_key,
    get_audit_logs_for_model
)

# -------------------------------
# Backup Services
# -------------------------------
def initiate_backup(backup_type, user=None):
    """
    Creates a new BackupRecord and marks it as in-progress.
    Actual backup logic should be handled by a background task.
    """
    backup = BackupRecord.objects.create(
        backup_type=backup_type,
        status='IN_PROGRESS',
        initiated_by=user,
        started_at=timezone.now()
    )
    return backup

def complete_backup(backup_id, file_path, file_size, metadata=None):
    """
    Marks a backup as completed and stores metadata.
    """
    backup = BackupRecord.objects.get(id=backup_id)
    backup.file_path = file_path
    backup.file_size = file_size
    backup.status = 'COMPLETED'
    backup.completed_at = timezone.now()
    backup.metadata = metadata or {}
    backup.save()
    return backup

def fail_backup(backup_id, error_message):
    """
    Marks a backup as failed and logs the error.
    """
    backup = BackupRecord.objects.get(id=backup_id)
    backup.status = 'FAILED'
    backup.error_message = error_message
    backup.completed_at = timezone.now()
    backup.save()
    return backup

# -------------------------------
# Configuration Services
# -------------------------------
def update_configuration_value(key, new_value, user=None):
    """
    Updates the value of a configuration key.
    """
    config = get_config_by_key(key)
    if not config:
        raise ValueError(f"Configuration key '{key}' not found.")
    
    config.value = new_value
    config.updated_at = timezone.now()
    config.save()

    log_system_event(
        level='INFO',
        category='SYSTEM',
        message=f"Configuration '{key}' updated to '{new_value}'",
        user=user
    )
    return config

# -------------------------------
# Logging Services
# -------------------------------
def log_system_event(level, category, message, user=None, ip=None, path=None, metadata=None):
    """
    Creates a new system log entry.
    """
    return SystemLog.objects.create(
        level=level,
        category=category,
        message=message,
        user=user,
        ip_address=ip,
        request_path=path,
        metadata=metadata or {}
    )

# -------------------------------
# Audit Trail Services
# -------------------------------
def record_audit_log(action, model_name, object_id, user=None, changes=None, object_repr='', ip=None, user_agent=None):
    """
    Records an audit log entry for compliance tracking.
    """
    return AuditLog.objects.create(
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        object_repr=object_repr,
        changes=changes or {},
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        created_at=timezone.now()
    )

def get_model_audit_summary(model_name):
    """
    Returns a summary of audit actions for a given model.
    """
    logs = get_audit_logs_for_model(model_name)
    summary = {}
    for log in logs:
        summary[log.action] = summary.get(log.action, 0) + 1
    return summary
