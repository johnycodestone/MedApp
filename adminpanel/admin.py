# adminpanel/admin.py

from django.contrib import admin
from .models import (
    SystemConfiguration,
    BackupRecord,
    SystemLog,
    RolePermission,
    SystemMetric,
    AuditLog
)

# -------------------------------
# Admin registration for SystemConfiguration
# -------------------------------
@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for SystemConfiguration.
    Manages system-wide key-value settings.
    """
    list_display = ('key', 'value', 'data_type', 'category', 'is_active', 'created_by', 'updated_at')
    search_fields = ('key', 'description')
    list_filter = ('data_type', 'category', 'is_active')
    ordering = ('category', 'key')

# -------------------------------
# Admin registration for BackupRecord
# -------------------------------
@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for BackupRecord.
    Tracks system backups and their status.
    """
    list_display = ('backup_type', 'status', 'file_size', 'started_at', 'completed_at', 'initiated_by')
    search_fields = ('file_path', 'error_message')
    list_filter = ('backup_type', 'status', 'started_at')
    ordering = ('-started_at',)

# -------------------------------
# Admin registration for SystemLog
# -------------------------------
@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for SystemLog.
    Displays system-wide logs for monitoring and debugging.
    """
    list_display = ('level', 'category', 'message', 'user', 'ip_address', 'created_at')
    search_fields = ('message', 'user__username', 'ip_address', 'request_path')
    list_filter = ('level', 'category', 'created_at')
    ordering = ('-created_at',)

# -------------------------------
# Admin registration for RolePermission
# -------------------------------
@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for RolePermission.
    Manages granular permissions for user roles.
    """
    list_display = ('role', 'permission_key', 'is_granted', 'updated_at')
    search_fields = ('permission_key', 'description')
    list_filter = ('role', 'is_granted')
    ordering = ('role', 'permission_key')

# -------------------------------
# Admin registration for SystemMetric
# -------------------------------
@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for SystemMetric.
    Displays system performance metrics over time.
    """
    list_display = ('metric_name', 'metric_value', 'metric_type', 'recorded_at')
    search_fields = ('metric_name',)
    list_filter = ('metric_type', 'recorded_at')
    ordering = ('-recorded_at',)

# -------------------------------
# Admin registration for AuditLog
# -------------------------------
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for AuditLog.
    Tracks detailed audit trails for compliance and monitoring.
    """
    list_display = ('action', 'model_name', 'object_id', 'user', 'ip_address', 'created_at')
    search_fields = ('model_name', 'object_id', 'user__username')
    list_filter = ('action', 'model_name', 'created_at')
    ordering = ('-created_at',)

# -------------------------------
# Custom admin site branding
# -------------------------------
admin.site.site_header = 'MedApp System Administration'
admin.site.site_title = 'MedApp System Admin Portal'
admin.site.index_title = 'Welcome to MedApp System Admin'
