# adminpanel/serializers.py

"""
DRF serializers for adminpanel system-level operations.
Handles validation and transformation for configurations, logs, backups, metrics, and audit trails.
"""

from rest_framework import serializers
from .models import (
    SystemConfiguration,
    BackupRecord,
    SystemLog,
    RolePermission,
    SystemMetric,
    AuditLog
)

# -------------------------------
# System Configuration Serializers
# -------------------------------
class SystemConfigurationSerializer(serializers.ModelSerializer):
    """
    Full serializer for system configuration entries.
    Includes typed value conversion and metadata.
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    typed_value = serializers.SerializerMethodField()

    class Meta:
        model = SystemConfiguration
        fields = [
            'id', 'key', 'value', 'typed_value', 'data_type',
            'description', 'category', 'category_display',
            'is_active', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_typed_value(self, obj):
        return obj.get_typed_value()

    def validate_key(self, value):
        if not self.instance and SystemConfiguration.objects.filter(key=value).exists():
            raise serializers.ValidationError("Configuration key already exists.")
        return value

class SystemConfigurationUpdateSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for updating config values only.
    """
    class Meta:
        model = SystemConfiguration
        fields = ['value', 'is_active']

# -------------------------------
# Backup Record Serializers
# -------------------------------
class BackupRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for backup records with computed fields.
    """
    backup_type_display = serializers.CharField(source='get_backup_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = BackupRecord
        fields = [
            'id', 'backup_type', 'backup_type_display',
            'file_path', 'file_size', 'file_size_mb',
            'status', 'status_display', 'error_message',
            'initiated_by', 'initiated_by_username',
            'started_at', 'completed_at', 'duration_seconds',
            'metadata'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']

    def get_duration_seconds(self, obj):
        return obj.duration()

    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0

class BackupInitiateSerializer(serializers.Serializer):
    """
    Serializer for initiating a backup operation.
    """
    backup_type = serializers.ChoiceField(choices=BackupRecord.BACKUP_TYPES, required=True)

class RestoreBackupSerializer(serializers.Serializer):
    """
    Serializer for restoring from a backup.
    """
    backup_id = serializers.IntegerField(required=True)
    confirm = serializers.BooleanField(required=True)

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("You must confirm the restore operation.")
        return value

# -------------------------------
# System Log Serializer
# -------------------------------
class SystemLogSerializer(serializers.ModelSerializer):
    """
    Serializer for system logs with metadata and user info.
    """
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SystemLog
        fields = [
            'id', 'level', 'level_display', 'category', 'category_display',
            'message', 'user', 'user_username', 'ip_address',
            'user_agent', 'request_path', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

# -------------------------------
# Role Permission Serializer
# -------------------------------
class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for role-based permission entries.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_display', 'permission_key',
            'description', 'is_granted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# -------------------------------
# System Metric Serializer
# -------------------------------
class SystemMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for system performance metrics.
    """
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)

    class Meta:
        model = SystemMetric
        fields = [
            'id', 'metric_name', 'metric_value', 'metric_type',
            'metric_type_display', 'tags', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']

# -------------------------------
# Audit Log Serializer
# -------------------------------
class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit trail entries.
    """
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_display', 'model_name',
            'object_id', 'object_repr', 'changes',
            'user', 'user_username',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
