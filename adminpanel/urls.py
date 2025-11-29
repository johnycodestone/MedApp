# adminpanel/urls.py
# COMPLETE ADMIN PANEL URLS - REPLACE YOUR ENTIRE FILE WITH THIS

from django.urls import path, include
from django.contrib.admin import site
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Django Admin Site
    path('django-admin/', site.urls, name='django-admin'),

    # ========================================
    # MAIN DASHBOARD
    # ========================================
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # ========================================
    # USER MANAGEMENT
    # ========================================
    path('users/', views.users_list, name='users-list'),
    path('doctors/', views.doctors_list, name='doctors-list'),
    path('patients/', views.patients_list, name='patients-list'),
    path('hospitals/', views.hospitals_list, name='hospitals-list'),
    
    # ========================================
    # SYSTEM MANAGEMENT
    # ========================================
    path('configs/', views.configs_view, name='configs'),
    path('backups/', views.backups_view, name='backups'),
    path('logs/', views.logs_view, name='logs'),
    path('audit/', views.audit_view, name='audit'),
    
    # ========================================
    # CONTENT MANAGEMENT
    # ========================================
    path('prescriptions/', views.prescriptions_admin_list, name='prescriptions-list'),
    path('appointments/', views.appointments_admin_list, name='appointments-list'),
    path('departments/', views.departments_list, name='departments-list'),
    
    # ========================================
    # SETTINGS
    # ========================================
    path('settings/email/', views.email_settings, name='email-settings'),
    path('settings/notifications/', views.notifications_settings, name='notifications'),
    path('settings/security/', views.security_settings, name='security'),

    # ========================================
    # API ENDPOINTS
    # ========================================
    path('api/system/', include([
        path('metrics-summary/', views.system_metrics_summary, name='system-metrics-summary'),
        path('config-summary/', views.config_summary_view, name='config-summary'),
        path('audit-log-stats/', views.audit_log_stats_view, name='audit-log-stats'),
        path('user-stats/', views.user_stats_api, name='user-stats'),
    ])),

    # ========================================
    # AUTHENTICATION ROUTES
    # ========================================
    path('api/auth/', include([
        path('login/', views.admin_login_view, name='admin-login'),
        path('logout/', views.admin_logout_view, name='admin-logout'),
        path('password-reset/', views.admin_password_reset_view, name='admin-password-reset'),
    ])),
]

# ========================================
# CUSTOM ERROR HANDLERS
# ========================================
handler400 = 'adminpanel.views.bad_request'
handler403 = 'adminpanel.views.permission_denied'
handler404 = 'adminpanel.views.page_not_found'
handler500 = 'adminpanel.views.server_error'
