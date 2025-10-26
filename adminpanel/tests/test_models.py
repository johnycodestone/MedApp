# adminpanel/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from adminpanel.models import (
    SystemConfiguration, BackupRecord, SystemLog,
    RolePermission, SystemMetric, AuditLog
)

User = get_user_model()

class SystemConfigurationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='configuser', password='pass123')
        self.config = SystemConfiguration.objects.create(
            key='enable_feature_x',
            value='true',
            data_type='BOOLEAN',
            description='Enable feature X',
            category='FEATURE',
            is_active=True,
            created_by=self.user
        )

    def test_config_creation(self):
        self.assertEqual(self.config.key, 'enable_feature_x')
        self.assertTrue(self.config.is_active)

    def test_config_str_method(self):
        self.assertIn('enable_feature_x', str(self.config))

    def test_typed_value_boolean(self):
        self.assertTrue(self.config.get_typed_value())

    def test_unique_key_constraint(self):
        with self.assertRaises(Exception):
            SystemConfiguration.objects.create(
                key='enable_feature_x',
                value='false'
            )

class BackupRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='backupuser', password='pass123')
        self.backup = BackupRecord.objects.create(
            backup_type='DATABASE',
            file_path='/backups/db_2025.sql',
            file_size=204800,
            status='COMPLETED',
            initiated_by=self.user,
            started_at=timezone.now() - timedelta(minutes=10),
            completed_at=timezone.now()
        )

    def test_backup_creation(self):
        self.assertEqual(self.backup.backup_type, 'DATABASE')
        self.assertEqual(self.backup.status, 'COMPLETED')

    def test_backup_str_method(self):
        self.assertIn('Database Backup', str(self.backup))

    def test_backup_duration(self):
        self.assertTrue(self.backup.duration() > 0)

class SystemLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='loguser', password='pass123')
        self.log = SystemLog.objects.create(
            level='ERROR',
            category='AUTHENTICATION',
            message='Failed login attempt',
            user=self.user,
            ip_address='192.168.1.1',
            request_path='/login'
        )

    def test_log_creation(self):
        self.assertEqual(self.log.level, 'ERROR')
        self.assertEqual(self.log.category, 'AUTHENTICATION')

    def test_log_str_method(self):
        self.assertIn('[ERROR]', str(self.log))

class RolePermissionModelTest(TestCase):
    def setUp(self):
        self.permission = RolePermission.objects.create(
            role='DOCTOR',
            permission_key='can_view_records',
            description='Allows viewing patient records',
            is_granted=True
        )

    def test_permission_creation(self):
        self.assertEqual(self.permission.role, 'DOCTOR')
        self.assertTrue(self.permission.is_granted)

    def test_permission_str_method(self):
        self.assertIn('Doctor', str(self.permission))

    def test_unique_role_permission_key(self):
        with self.assertRaises(Exception):
            RolePermission.objects.create(
                role='DOCTOR',
                permission_key='can_view_records'
            )

class SystemMetricModelTest(TestCase):
    def setUp(self):
        self.metric = SystemMetric.objects.create(
            metric_name='active_users',
            metric_value=123,
            metric_type='GAUGE',
            tags={'region': 'PK'}
        )

    def test_metric_creation(self):
        self.assertEqual(self.metric.metric_name, 'active_users')
        self.assertEqual(self.metric.metric_value, 123)

    def test_metric_str_method(self):
        self.assertIn('active_users', str(self.metric))

class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='audituser', password='pass123')
        self.audit = AuditLog.objects.create(
            action='UPDATE',
            model_name='SystemConfiguration',
            object_id='config_001',
            object_repr='enable_feature_x',
            changes={'value': ['false', 'true']},
            user=self.user,
            ip_address='127.0.0.1'
        )

    def test_audit_creation(self):
        self.assertEqual(self.audit.action, 'UPDATE')
        self.assertEqual(self.audit.model_name, 'SystemConfiguration')

    def test_audit_str_method(self):
        self.assertIn('UPDATE', str(self.audit))
