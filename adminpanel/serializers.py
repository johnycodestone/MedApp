"""
adminpanel/serializers.py

DRF serializers for admin panel operations.
Handles validation and data transformation for admin endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SystemConfiguration, BackupRecord, SystemLog,
    RolePermission, SystemMetric, AuditLog,
    User,
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    Prescription
)

User = get_user_model()


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for system configuration settings.
    """
    
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    
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
        """Return properly typed value"""
        return obj.get_typed_value()
    
    def validate_key(self, value):
        """Ensure key is unique when creating"""
        if not self.instance:  # Creating new
            if SystemConfiguration.objects.filter(key=value).exists():
                raise serializers.ValidationError("Configuration key already exists.")
        return value


class SystemConfigurationUpdateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for updating configuration values.
    """
    
    class Meta:
        model = SystemConfiguration
        fields = ['value', 'is_active']


class BackupRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for backup records.
    """
    
    backup_type_display = serializers.CharField(
        source='get_backup_type_display',
        read_only=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    initiated_by_username = serializers.CharField(
        source='initiated_by.username',
        read_only=True
    )
    
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
        """Calculate backup duration"""
        return obj.duration()
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class BackupInitiateSerializer(serializers.Serializer):
    """
    Serializer for initiating backups.
    """
    
    backup_type = serializers.ChoiceField(
        choices=BackupRecord.BACKUP_TYPES,
        required=True
    )


class SystemLogSerializer(serializers.ModelSerializer):
    """
    Serializer for system logs.
    """
    
    level_display = serializers.CharField(
        source='get_level_display',
        read_only=True
    )
    
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    
    class Meta:
        model = SystemLog
        fields = [
            'id', 'level', 'level_display', 'category', 'category_display',
            'message', 'user', 'user_username', 'ip_address',
            'user_agent', 'request_path', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for role permissions.
    """
    
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_display', 'permission_key',
            'description', 'is_granted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for system metrics.
    """
    
    metric_type_display = serializers.CharField(
        source='get_metric_type_display',
        read_only=True
    )
    
    class Meta:
        model = SystemMetric
        fields = [
            'id', 'metric_name', 'metric_value', 'metric_type',
            'metric_type_display', 'tags', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit logs.
    """
    
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True
    )
    
    user_username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    
    user_role = serializers.CharField(
        source='user.role',
        read_only=True
    )
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_display', 'model_name',
            'object_id', 'object_repr', 'changes',
            'user', 'user_username', 'user_role',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserManagementSerializer(serializers.ModelSerializer):
    """
    Serializer for user management in admin panel.
    """
    
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True
    )
    
    profile_complete = serializers.SerializerMethodField()
    last_login_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'role_display', 'is_active',
            'is_verified', 'is_staff', 'is_superuser',
            'last_login', 'last_login_display', 'date_joined',
            'profile_complete'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_profile_complete(self, obj):
        """Check if user profile is complete"""
        return bool(obj.first_name and obj.last_name and obj.email)
    
    def get_last_login_display(self, obj):
        """Format last login"""
        if obj.last_login:
            from django.utils.timesince import timesince
            return f"{timesince(obj.last_login)} ago"
        return "Never"


class UserActivationSerializer(serializers.Serializer):
    """
    Serializer for activating/deactivating users.
    """
    
    user_id = serializers.IntegerField(required=True)
    is_active = serializers.BooleanField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class BulkUserActionSerializer(serializers.Serializer):
    """
    Serializer for bulk user actions.
    """
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    
    action = serializers.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('verify', 'Verify'),
            ('delete', 'Delete')
        ],
        required=True
    )


class SystemStatsSerializer(serializers.Serializer):
    """
    Serializer for system statistics.
    """
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    users_by_role = serializers.DictField()
    
    total_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    
    total_doctors = serializers.IntegerField()
    active_doctors = serializers.IntegerField()
    
    total_hospitals = serializers.IntegerField()
    active_hospitals = serializers.IntegerField()
    
    recent_backups = serializers.IntegerField()
    failed_backups = serializers.IntegerField()
    
    error_logs_count = serializers.IntegerField()
    warning_logs_count = serializers.IntegerField()


class RestoreBackupSerializer(serializers.Serializer):
    """
    Serializer for restoring from backup.
    """
    
    backup_id = serializers.IntegerField(required=True)
    confirm = serializers.BooleanField(required=True)
    
    def validate_confirm(self, value):
        """Ensure confirmation is true"""
        if not value:
            raise serializers.ValidationError("You must confirm the restore operation.")
        return value

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with admin-level details
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
        read_only_fields = ['is_staff', 'is_active']

class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model with comprehensive details
    """
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        extra_kwargs = {
            'contact_number': {'validators': []}  # Remove default validators if any
        }
    
    def validate_contact_number(self, value):
        """
        Custom validation for contact number
        """
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must contain only digits")
        return value

class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model with comprehensive details
    """
    total_appointments = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = '__all__'
    
    def get_total_appointments(self, obj):
        """
        Method to get total appointments for a doctor
        """
        return obj.appointments.count()

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model with comprehensive details
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def validate(self, data):
        """
        Custom validation for appointments
        """
        patient = data.get('patient')
        doctor = data.get('doctor')
        
        if patient and doctor and patient == doctor:
            raise serializers.ValidationError("Patient cannot be the same as the doctor")
        
        return data

class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for MedicalRecord model with comprehensive details
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prescription model with comprehensive details
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
    
    def validate(self, data):
        """
        Custom validation for prescriptions
        """
        patient = data.get('patient')
        doctor = data.get('doctor')
        
        if not patient or not doctor:
            raise serializers.ValidationError("Both patient and doctor are required")
        
        return data