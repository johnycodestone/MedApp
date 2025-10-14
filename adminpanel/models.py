"""
adminpanel/models.py

Data models for system administration and monitoring.
Handles system logs, backups, configurations, and audit trails.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings.
    
    Stores key-value pairs for system configuration that can be
    modified without code changes.
    
    Fields:
    - key: Unique configuration key
    - value: Configuration value (stored as text)
    - data_type: Type of the value (STRING, INTEGER, BOOLEAN, JSON)
    - description: Human-readable description
    - is_active: Whether this config is currently active
    - category: Configuration category for grouping
    """
    
    DATA_TYPES = (
        ('STRING', 'String'),
        ('INTEGER', 'Integer'),
        ('BOOLEAN', 'Boolean'),
        ('JSON', 'JSON'),
        ('FLOAT', 'Float'),
    )
    
    CATEGORIES = (
        ('GENERAL', 'General Settings'),
        ('EMAIL', 'Email Configuration'),
        ('SECURITY', 'Security Settings'),
        ('NOTIFICATION', 'Notification Settings'),
        ('FEATURE', 'Feature Flags'),
        ('MAINTENANCE', 'Maintenance Mode'),
    )
    
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique configuration key"
    )
    
    value = models.TextField(
        help_text="Configuration value (stored as text)"
    )
    
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES,
        default='STRING',
        help_text="Data type of the value"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of this configuration"
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default='GENERAL',
        help_text="Configuration category"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is active"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_configs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.key} ({self.get_category_display()})"
    
    def get_typed_value(self):
        """Return value with proper type conversion"""
        if self.data_type == 'INTEGER':
            return int(self.value)
        elif self.data_type == 'FLOAT':
            return float(self.value)
        elif self.data_type == 'BOOLEAN':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.data_type == 'JSON':
            import json
            return json.loads(self.value)
        return self.value


class BackupRecord(models.Model):
    """
    Records of system backups.
    
    Tracks database backups, file backups, and their status.
    
    Fields:
    - backup_type: Type of backup (DATABASE, FILES, FULL)
    - file_path: Path to backup file
    - file_size: Size of backup in bytes
    - status: Backup status
    - started_at: Backup start time
    - completed_at: Backup completion time
    """
    
    BACKUP_TYPES = (
        ('DATABASE', 'Database Backup'),
        ('FILES', 'File Backup'),
        ('FULL', 'Full System Backup'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    backup_type = models.CharField(
        max_length=20,
        choices=BACKUP_TYPES,
        help_text="Type of backup"
    )
    
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to backup file"
    )
    
    file_size = models.BigIntegerField(
        default=0,
        help_text="Backup file size in bytes"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Backup status"
    )
    
    error_message = models.TextField(
        blank=True,
        help_text="Error message if backup failed"
    )
    
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_backups'
    )
    
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="Backup start timestamp"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Backup completion timestamp"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional backup metadata"
    )
    
    class Meta:
        db_table = 'backup_records'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['backup_type']),
        ]
    
    def __str__(self):
        return f"{self.get_backup_type_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def duration(self):
        """Calculate backup duration"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class SystemLog(models.Model):
    """
    System-wide event logs.
    
    Logs important system events for monitoring and debugging.
    
    Fields:
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - category: Log category
    - message: Log message
    - user: User associated with the event (if any)
    - ip_address: IP address of the request
    """
    
    LOG_LEVELS = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )
    
    CATEGORIES = (
        ('AUTHENTICATION', 'Authentication'),
        ('AUTHORIZATION', 'Authorization'),
        ('DATABASE', 'Database'),
        ('BACKUP', 'Backup'),
        ('SECURITY', 'Security'),
        ('PERFORMANCE', 'Performance'),
        ('SYSTEM', 'System'),
        ('API', 'API'),
    )
    
    level = models.CharField(
        max_length=20,
        choices=LOG_LEVELS,
        help_text="Log severity level"
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        help_text="Log category"
    )
    
    message = models.TextField(
        help_text="Log message"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    
    request_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Request URL path"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional log context"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"


class RolePermission(models.Model):
    """
    Custom role-based permissions.
    
    Defines granular permissions for different user roles.
    
    Fields:
    - role: User role (HOSPITAL, DOCTOR, PATIENT, ADMIN)
    - permission_key: Unique permission identifier
    - description: Permission description
    - is_granted: Whether permission is granted
    """
    
    ROLES = (
        ('HOSPITAL', 'Hospital'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Administrator'),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        help_text="User role"
    )
    
    permission_key = models.CharField(
        max_length=100,
        help_text="Unique permission key (e.g., 'can_delete_appointments')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Human-readable permission description"
    )
    
    is_granted = models.BooleanField(
        default=False,
        help_text="Whether this permission is granted to the role"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'role_permissions'
        ordering = ['role', 'permission_key']
        unique_together = ['role', 'permission_key']
        indexes = [
            models.Index(fields=['role', 'is_granted']),
        ]
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.permission_key}"


class SystemMetric(models.Model):
    """
    System performance metrics.
    
    Tracks system health and performance metrics over time.
    
    Fields:
    - metric_name: Name of the metric
    - metric_value: Numeric value
    - metric_type: Type of metric (COUNTER, GAUGE, HISTOGRAM)
    - tags: Additional tags for filtering (JSON)
    """
    
    METRIC_TYPES = (
        ('COUNTER', 'Counter'),
        ('GAUGE', 'Gauge'),
        ('HISTOGRAM', 'Histogram'),
    )
    
    metric_name = models.CharField(
        max_length=100,
        help_text="Metric name (e.g., 'active_users', 'response_time')"
    )
    
    metric_value = models.FloatField(
        help_text="Metric value"
    )
    
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        default='GAUGE',
        help_text="Metric type"
    )
    
    tags = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional tags for filtering"
    )
    
    recorded_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        db_table = 'system_metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_name', '-recorded_at']),
            models.Index(fields=['metric_type']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value}"


class AuditLog(models.Model):
    """
    Detailed audit trail for compliance.
    
    Records all significant system changes for audit purposes.
    
    Fields:
    - action: Type of action performed
    - model_name: Name of the affected model
    - object_id: ID of the affected object
    - changes: JSON representation of changes
    - user: User who performed the action
    """
    
    ACTIONS = (
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('EXPORT', 'Exported'),
        ('IMPORT', 'Imported'),
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTIONS,
        help_text="Action performed"
    )
    
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the affected model"
    )
    
    object_id = models.CharField(
        max_length=100,
        help_text="ID of the affected object"
    )
    
    object_repr = models.CharField(
        max_length=200,
        blank=True,
        help_text="String representation of the object"
    )
    
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON of changes made"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model_name} #{self.object_id}"