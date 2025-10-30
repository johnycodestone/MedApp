# adminpanel/repositories.py

"""
Repository layer for adminpanel models.
Encapsulates reusable query logic for system-level data access.
"""

from .models import (
    SystemConfiguration,
    BackupRecord,
    SystemLog,
    RolePermission,
    SystemMetric,
    AuditLog
)
from django.db.models import Count, Q
from django.utils import timezone


# -------------------------------
# SystemConfiguration Queries
# -------------------------------
def get_active_configurations():
    """
    Returns all active system configurations.
    """
    return SystemConfiguration.objects.filter(is_active=True)

def get_config_by_key(key):
    """
    Returns a configuration by its key (case-insensitive).
    """
    return SystemConfiguration.objects.filter(key__iexact=key).first()


# -------------------------------
# BackupRecord Queries
# -------------------------------
def get_recent_backups(limit=5):
    """
    Returns the most recent backup records.
    """
    return BackupRecord.objects.order_by('-started_at')[:limit]

def get_failed_backups():
    """
    Returns all backups that failed.
    """
    return BackupRecord.objects.filter(status='FAILED')


# -------------------------------
# SystemLog Queries
# -------------------------------
def get_logs_by_level(level):
    """
    Returns logs filtered by severity level.
    """
    return SystemLog.objects.filter(level=level).order_by('-created_at')

def get_logs_for_user(user):
    """
    Returns logs associated with a specific user.
    """
    return SystemLog.objects.filter(user=user).order_by('-created_at')


# -------------------------------
# RolePermission Queries
# -------------------------------
def get_permissions_for_role(role):
    """
    Returns all permissions granted to a specific role.
    """
    return RolePermission.objects.filter(role=role, is_granted=True)


# -------------------------------
# SystemMetric Queries
# -------------------------------
def get_latest_metrics(metric_name, limit=10):
    """
    Returns the latest metric entries for a given metric name.
    """
    return SystemMetric.objects.filter(metric_name=metric_name).order_by('-recorded_at')[:limit]

def get_metric_summary():
    """
    Returns a count of metrics grouped by type.
    """
    return SystemMetric.objects.values('metric_type').annotate(count=Count('id'))


# -------------------------------
# AuditLog Queries
# -------------------------------
def get_audit_logs_for_model(model_name):
    """
    Returns audit logs for a specific model.
    """
    return AuditLog.objects.filter(model_name=model_name).order_by('-created_at')

def get_audit_logs_by_action(action):
    """
    Returns audit logs filtered by action type.
    """
    return AuditLog.objects.filter(action=action).order_by('-created_at')
