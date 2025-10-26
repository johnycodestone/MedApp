# adminpanel/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from adminpanel.models import (
    SystemConfiguration, BackupRecord, SystemLog,
    SystemMetric, AuditLog
)

User = get_user_model()

class AdminPanelViewsTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.client = Client()
        self.client.login(username='admin', password='adminpass123')

        # Seed minimal data
        SystemConfiguration.objects.create(
            key='enable_feature_x',
            value='true',
            data_type='BOOLEAN',
            category='FEATURE',
            is_active=True,
            created_by=self.admin_user
        )

        BackupRecord.objects.create(
            backup_type='DATABASE',
            status='COMPLETED',
            initiated_by=self.admin_user,
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        SystemLog.objects.create(
            level='INFO',
            category='SYSTEM',
            message='System started',
            user=self.admin_user
        )

        SystemMetric.objects.create(
            metric_name='active_users',
            metric_value=42,
            metric_type='GAUGE'
        )

        AuditLog.objects.create(
            action='CREATE',
            model_name='SystemConfiguration',
            object_id='config_001',
            user=self.admin_user
        )

    def test_admin_dashboard_view(self):
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adminpanel/dashboard.html')
        self.assertIn('active_configs', response.context)
        self.assertIn('recent_logs', response.context)
        self.assertIn('recent_backups', response.context)
        self.assertIn('total_audit_logs', response.context)

    def test_system_metrics_summary_api(self):
        response = self.client.get(reverse('system-metrics-summary'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('metric_summary', response.json())

    def test_config_summary_view_api(self):
        response = self.client.get(reverse('config-summary'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('active_config_summary', response.json())

    def test_audit_log_stats_view_api(self):
        response = self.client.get(reverse('audit-log-stats'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('audit_action_summary', response.json())

    def test_unauthorized_access_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        response = self.client.get(reverse('system-metrics-summary'))
        self.assertEqual(response.status_code, 302)

    def test_error_handlers(self):
        # Simulate error handler calls manually
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)

        # These would be triggered by Django internally, so we just confirm handlers exist
        from adminpanel.views import bad_request, permission_denied, page_not_found, server_error
        self.assertTrue(callable(bad_request))
        self.assertTrue(callable(permission_denied))
        self.assertTrue(callable(page_not_found))
        self.assertTrue(callable(server_error))
