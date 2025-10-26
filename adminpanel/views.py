# adminpanel/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.db.models import Count

from .models import (
    SystemConfiguration,
    BackupRecord,
    SystemLog,
    RolePermission,
    SystemMetric,
    AuditLog
)

# -------------------------------
# Admin Dashboard View
# -------------------------------
class AdminDashboardView(TemplateView):
    """
    System-level admin dashboard view.
    Displays high-level system metrics and recent logs.
    """
    template_name = 'adminpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_configs'] = SystemConfiguration.objects.filter(is_active=True).count()
        context['recent_logs'] = SystemLog.objects.order_by('-created_at')[:5]
        context['recent_backups'] = BackupRecord.objects.order_by('-started_at')[:3]
        context['total_audit_logs'] = AuditLog.objects.count()
        return context

# -------------------------------
# System Metrics Summary API
# -------------------------------
@staff_member_required
def system_metrics_summary(request):
    """
    Returns a summary of system metrics (e.g., counters, gauges).
    """
    metric_counts = SystemMetric.objects.values('metric_type').annotate(count=Count('id'))
    return JsonResponse({'metric_summary': list(metric_counts)})

# -------------------------------
# Configuration Overview API
# -------------------------------
@staff_member_required
def config_summary_view(request):
    """
    Returns a summary of active system configurations grouped by category.
    """
    config_counts = SystemConfiguration.objects.filter(is_active=True).values('category').annotate(count=Count('id'))
    return JsonResponse({'active_config_summary': list(config_counts)})

# -------------------------------
# Audit Log Statistics API
# -------------------------------
@staff_member_required
def audit_log_stats_view(request):
    """
    Returns statistics about audit log actions.
    """
    action_counts = AuditLog.objects.values('action').annotate(count=Count('id'))
    return JsonResponse({'audit_action_summary': list(action_counts)})

# -------------------------------
# Error Handler Views
# -------------------------------
def bad_request(request, exception):
    """Custom 400 error handler"""
    return render(request, 'adminpanel/errors/400.html', status=400)

def permission_denied(request, exception):
    """Custom 403 error handler"""
    return render(request, 'adminpanel/errors/403.html', status=403)

def page_not_found(request, exception):
    """Custom 404 error handler"""
    return render(request, 'adminpanel/errors/404.html', status=404)

def server_error(request):
    """Custom 500 error handler"""
    return render(request, 'adminpanel/errors/500.html', status=500)

# -------------------------------
# Admin Authentication Views
# -------------------------------
@staff_member_required
def admin_login_view(request):
    """
    Custom admin login view with additional security checks.
    Placeholder for future implementation.
    """
    pass

@login_required
def admin_logout_view(request):
    """
    Custom admin logout view.
    Placeholder for future implementation.
    """
    pass

@staff_member_required
def admin_password_reset_view(request):
    """
    Custom admin password reset view.
    Placeholder for future implementation.
    """
    pass
