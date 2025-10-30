# adminpanel/tests/test_services.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from adminpanel.models import (
    BackupRecord, SystemConfiguration, SystemLog, AuditLog
)
from adminpanel.services import (
    initiate_backup, complete_backup, fail_backup,
    update_configuration_value, log_system_event,
    record_audit_log, get_model_audit_summary
)

User = get_user_model()

class AdminPanelServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='adminpass123')
        self.config = SystemConfiguration.objects.create(
            key='feature_toggle',
            value='false',
            data_type='BOOLEAN',
            category='FEATURE',
            is_active=True,
            created_by=self.user
        )
        self.backup = initiate_backup('DATABASE', user=self.user)

    def test_initiate_backup(self):
        self.assertEqual(self.backup.status, 'IN_PROGRESS')
        self.assertEqual(self.backup.backup_type, 'DATABASE')
        self.assertEqual(self.backup.initiated_by, self.user)

    def test_complete_backup(self):
        updated = complete_backup(
            backup_id=self.backup.id,
            file_path='/backups/db.sql',
            file_size=204800,
            metadata={'note': 'nightly backup'}
        )
        self.assertEqual(updated.status, 'COMPLETED')
        self.assertEqual(updated.file_path, '/backups/db.sql')
        self.assertEqual(updated.metadata['note'], 'nightly backup')

    def test_fail_backup(self):
        failed = fail_backup(self.backup.id, error_message='Disk full')
        self.assertEqual(failed.status, 'FAILED')
        self.assertEqual(failed.error_message, 'Disk full')

    def test_update_configuration_value(self):
        updated = update_configuration_value('feature_toggle', 'true', user=self.user)
        self.assertEqual(updated.value, 'true')
        log = SystemLog.objects.last()
        self.assertIn("Configuration 'feature_toggle' updated", log.message)

    def test_log_system_event(self):
        log = log_system_event(
            level='WARNING',
            category='SECURITY',
            message='Suspicious login attempt',
            user=self.user,
            ip='192.168.1.1',
            path='/login',
            metadata={'attempts': 3}
        )
        self.assertEqual(log.level, 'WARNING')
        self.assertEqual(log.category, 'SECURITY')
        self.assertEqual(log.metadata['attempts'], 3)

    def test_record_audit_log(self):
        audit = record_audit_log(
            action='UPDATE',
            model_name='SystemConfiguration',
            object_id=self.config.id,
            user=self.user,
            changes={'value': ['false', 'true']},
            object_repr='feature_toggle',
            ip='127.0.0.1',
            user_agent='TestAgent'
        )
        self.assertEqual(audit.action, 'UPDATE')
        self.assertEqual(audit.model_name, 'SystemConfiguration')
        self.assertEqual(audit.changes['value'], ['false', 'true'])

    def test_get_model_audit_summary(self):
        record_audit_log(
            action='CREATE',
            model_name='SystemConfiguration',
            object_id='config_001',
            user=self.user
        )
        record_audit_log(
            action='UPDATE',
            model_name='SystemConfiguration',
            object_id='config_001',
            user=self.user
        )
        summary = get_model_audit_summary('SystemConfiguration')
        self.assertEqual(summary['CREATE'], 1)
        self.assertEqual(summary['UPDATE'], 1)
