# adminpanel/views.py
# COMPLETE ADMIN PANEL VIEWS - REPLACE YOUR ENTIRE FILE WITH THIS

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib import messages
from accounts.models import CustomUser

from .models import (
    SystemConfiguration,
    BackupRecord,
    SystemLog,
    RolePermission,
    SystemMetric,
    AuditLog
)

# ========================================
# DASHBOARD VIEW
# ========================================
class AdminDashboardView(TemplateView):
    """
    System-level admin dashboard view.
    Displays high-level system metrics and recent logs.
    """
    template_name = 'adminpanel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all users count
        from accounts.models import CustomUser
        context['total_users'] = CustomUser.objects.count()
        
        # Get appointments count (with error handling)
        try:
            from appointments.models import Appointment
            context['total_appointments'] = Appointment.objects.count()
        except:
            context['total_appointments'] = 0
        
        # Get prescriptions count (with error handling)
        try:
            from prescriptions.models import Prescription
            context['total_prescriptions'] = Prescription.objects.count()
        except:
            context['total_prescriptions'] = 0
        
        # System configurations
        context['active_configs'] = SystemConfiguration.objects.filter(is_active=True).count()
        
        # Recent logs
        context['recent_logs'] = SystemLog.objects.order_by('-created_at')[:5]
        
        # Recent backups
        context['recent_backups'] = BackupRecord.objects.order_by('-started_at')[:3]
        
        # Audit logs count
        context['total_audit_logs'] = AuditLog.objects.count()
        
        return context

# ========================================
# USER MANAGEMENT VIEWS
# ========================================
@staff_member_required
def users_list(request):
    """View all users with filters"""
    users = CustomUser.objects.all().order_by('-created_at')
    
    # Apply filters
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'verified':
        users = users.filter(is_verified=True)
    elif status_filter == 'unverified':
        users = users.filter(is_verified=False)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'adminpanel/users_list.html', context)

@staff_member_required
def doctors_list(request):
    """View all doctors"""
    try:
        from accounts.models import DoctorProfile
        doctors = DoctorProfile.objects.select_related('user').all()
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            doctors = doctors.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(specialization__icontains=search)
            )
        
        context = {
            'doctors': doctors,
            'active_doctors': doctors.filter(user__is_active=True).count(),
            'pending_doctors': doctors.filter(user__is_verified=False).count(),
            'search': search,
        }
    except Exception as e:
        context = {
            'doctors': [],
            'active_doctors': 0,
            'pending_doctors': 0,
            'error': str(e)
        }
    
    return render(request, 'adminpanel/doctors_list.html', context)

@staff_member_required
def patients_list(request):
    """View all patients"""
    try:
        from accounts.models import PatientProfile
        patients = PatientProfile.objects.select_related('user').all()
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            patients = patients.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        context = {
            'patients': patients,
            'active_patients': patients.filter(user__is_active=True).count(),
            'search': search,
        }
    except Exception as e:
        context = {
            'patients': [],
            'active_patients': 0,
            'error': str(e)
        }
    
    return render(request, 'adminpanel/patients_list.html', context)

@staff_member_required
def hospitals_list(request):
    """View all hospitals"""
    try:
        from accounts.models import HospitalProfile
        hospitals = HospitalProfile.objects.select_related('user').all()
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            hospitals = hospitals.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(hospital_name__icontains=search)
            )
        
        context = {
            'hospitals': hospitals,
            'active_hospitals': hospitals.filter(user__is_active=True).count(),
            'search': search,
        }
    except Exception as e:
        context = {
            'hospitals': [],
            'active_hospitals': 0,
            'error': str(e)
        }
    
    return render(request, 'adminpanel/hospitals_list.html', context)

# ========================================
# SYSTEM VIEWS
# ========================================
@staff_member_required
def configs_view(request):
    """View system configurations"""
    configurations = SystemConfiguration.objects.all()
    
    # Apply category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        configurations = configurations.filter(category=category_filter)
    
    # Get all categories
    categories = SystemConfiguration.objects.values_list('category', flat=True).distinct()
    
    context = {
        'configurations': configurations,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'adminpanel/configs.html', context)

@staff_member_required
def backups_view(request):
    """View and manage backups"""
    backups = BackupRecord.objects.all().order_by('-started_at')
    
    context = {
        'backups': backups,
        'completed_backups': backups.filter(status='COMPLETED').count(),
        'pending_backups': backups.filter(status='IN_PROGRESS').count(),
        'failed_backups': backups.filter(status='FAILED').count(),
        'total_size': '0 MB',
    }
    return render(request, 'adminpanel/backups.html', context)

@staff_member_required
def logs_view(request):
    """View system logs"""
    logs = SystemLog.objects.all().order_by('-created_at')
    
    # Apply filters
    level_filter = request.GET.get('level', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    if category_filter:
        logs = logs.filter(category=category_filter)
    
    if search:
        logs = logs.filter(
            Q(message__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Limit to last 100
    logs = logs[:100]
    
    context = {
        'logs': logs,
        'error_count': logs.filter(level='ERROR').count(),
        'warning_count': logs.filter(level='WARNING').count(),
        'info_count': logs.filter(level='INFO').count(),
        'debug_count': logs.filter(level='DEBUG').count(),
        'level_filter': level_filter,
        'category_filter': category_filter,
        'search': search,
    }
    return render(request, 'adminpanel/logs.html', context)

@staff_member_required
def audit_view(request):
    """View audit trail"""
    audit_logs = AuditLog.objects.all().order_by('-created_at')
    
    # Apply filters
    action_filter = request.GET.get('action', '')
    model_filter = request.GET.get('model', '')
    search = request.GET.get('search', '')
    
    if action_filter:
        audit_logs = audit_logs.filter(action=action_filter)
    
    if model_filter:
        audit_logs = audit_logs.filter(model_name=model_filter)
    
    if search:
        audit_logs = audit_logs.filter(
            Q(user__username__icontains=search) |
            Q(model_name__icontains=search) |
            Q(object_repr__icontains=search)
        )
    
    # Limit to last 100
    audit_logs = audit_logs[:100]
    
    context = {
        'audit_logs': audit_logs,
        'create_count': audit_logs.filter(action='CREATE').count(),
        'update_count': audit_logs.filter(action='UPDATE').count(),
        'delete_count': audit_logs.filter(action='DELETE').count(),
        'view_count': audit_logs.filter(action='VIEW').count(),
        'total_pages': 1,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'search': search,
    }
    return render(request, 'adminpanel/audit.html', context)

# ========================================
# CONTENT MANAGEMENT VIEWS
# ========================================
@staff_member_required
def prescriptions_admin_list(request):
    """View all prescriptions"""
    try:
        from prescriptions.models import Prescription
        prescriptions = Prescription.objects.select_related(
            'doctor__user', 
            'patient__user'
        ).all().order_by('-created_at')
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            prescriptions = prescriptions.filter(
                Q(doctor__user__username__icontains=search) |
                Q(patient__user__username__icontains=search) |
                Q(notes__icontains=search)
            )
        
        context = {
            'prescriptions': prescriptions,
            'search': search,
        }
    except Exception as e:
        context = {
            'prescriptions': [],
            'error': str(e)
        }
    
    return render(request, 'adminpanel/prescriptions_list.html', context)

@staff_member_required
def appointments_admin_list(request):
    """View all appointments"""
    try:
        from appointments.models import Appointment
        appointments = Appointment.objects.select_related(
            'doctor__user', 
            'patient__user'
        ).all().order_by('-created_at')
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            appointments = appointments.filter(
                Q(doctor__user__username__icontains=search) |
                Q(patient__user__username__icontains=search) |
                Q(reason__icontains=search)
            )
        
        context = {
            'appointments': appointments,
            'search': search,
        }
    except Exception as e:
        context = {
            'appointments': [],
            'error': str(e)
        }
    
    return render(request, 'adminpanel/appointments_list.html', context)

@staff_member_required
def departments_list(request):
    """View all departments"""
    try:
        from accounts.models import Department
        departments = Department.objects.all()
        
        # Apply search
        search = request.GET.get('search', '')
        if search:
            departments = departments.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        context = {
            'departments': departments,
            'search': search,
        }
    except Exception as e:
        context = {
            'departments': [],
            'error': str(e)
        }
    
    return render(request, 'adminpanel/departments_list.html', context)

# ========================================
# SETTINGS VIEWS
# ========================================
@staff_member_required
def email_settings(request):
    """Email configuration settings"""
    configs = SystemConfiguration.objects.filter(category='EMAIL')
    context = {
        'configurations': configs,
        'category': 'Email',
        'category_code': 'EMAIL'
    }
    return render(request, 'adminpanel/settings_generic.html', context)

@staff_member_required
def notifications_settings(request):
    """Notification settings"""
    configs = SystemConfiguration.objects.filter(category='NOTIFICATION')
    context = {
        'configurations': configs,
        'category': 'Notification',
        'category_code': 'NOTIFICATION'
    }
    return render(request, 'adminpanel/settings_generic.html', context)

@staff_member_required
def security_settings(request):
    """Security settings"""
    configs = SystemConfiguration.objects.filter(category='SECURITY')
    context = {
        'configurations': configs,
        'category': 'Security',
        'category_code': 'SECURITY'
    }
    return render(request, 'adminpanel/settings_generic.html', context)

# ========================================
# API VIEWS
# ========================================
@staff_member_required
def system_metrics_summary(request):
    """Returns a summary of system metrics (e.g., counters, gauges)."""
    metric_counts = SystemMetric.objects.values('metric_type').annotate(count=Count('id'))
    return JsonResponse({'metric_summary': list(metric_counts)})

@staff_member_required
def config_summary_view(request):
    """Returns a summary of active system configurations grouped by category."""
    config_counts = SystemConfiguration.objects.filter(is_active=True).values('category').annotate(count=Count('id'))
    return JsonResponse({'active_config_summary': list(config_counts)})

@staff_member_required
def audit_log_stats_view(request):
    """Returns statistics about audit log actions."""
    action_counts = AuditLog.objects.values('action').annotate(count=Count('id'))
    return JsonResponse({'audit_action_summary': list(action_counts)})

@staff_member_required
def user_stats_api(request):
    """API endpoint for user statistics"""
    from accounts.models import CustomUser
    
    # Get user counts by role
    user_stats = {
        'total': CustomUser.objects.count(),
        'patients': CustomUser.objects.filter(role='PATIENT').count(),
        'doctors': CustomUser.objects.filter(role='DOCTOR').count(),
        'hospitals': CustomUser.objects.filter(role='HOSPITAL').count(),
        'admins': CustomUser.objects.filter(role='ADMIN').count(),
    }
    
    # Get growth data (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    
    growth_data = []
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = CustomUser.objects.filter(created_at__date=date).count()
        growth_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return JsonResponse({
        'stats': user_stats,
        'growth': growth_data
    })

# ========================================
# ERROR HANDLER VIEWS
# ========================================
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

# ========================================
# AUTHENTICATION VIEWS (PLACEHOLDERS)
# ========================================
@staff_member_required
def admin_login_view(request):
    """Custom admin login view with additional security checks."""
    pass

@login_required
def admin_logout_view(request):
    """Custom admin logout view."""
    pass

@staff_member_required
def admin_password_reset_view(request):
    """Custom admin password reset view."""
    pass
