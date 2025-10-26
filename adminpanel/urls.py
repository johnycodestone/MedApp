# adminpanel/urls.py

from django.urls import path, include
from django.contrib.admin import site
from . import views
from .views import (
    AdminDashboardView,
    system_metrics_summary,
    config_summary_view,
    audit_log_stats_view,
    admin_login_view,
    admin_logout_view,
    admin_password_reset_view
)

# -------------------------------
# URL patterns for adminpanel
# -------------------------------
urlpatterns = [
    # Django Admin Site
    path('django-admin/', site.urls, name='django-admin'),

    # Admin Dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),

    # System-level API summaries
    path('api/system/', include([
        path('metrics-summary/', system_metrics_summary, name='system-metrics-summary'),
        path('config-summary/', config_summary_view, name='config-summary'),
        path('audit-log-stats/', audit_log_stats_view, name='audit-log-stats'),
    ])),

    # Authentication Routes
    path('api/auth/', include([
        path('login/', admin_login_view, name='admin-login'),
        path('logout/', admin_logout_view, name='admin-logout'),
        path('password-reset/', admin_password_reset_view, name='admin-password-reset'),
    ])),
]

# -------------------------------
# Custom error handlers
# -------------------------------
handler400 = 'adminpanel.views.bad_request'
handler403 = 'adminpanel.views.permission_denied'
handler404 = 'adminpanel.views.page_not_found'
handler500 = 'adminpanel.views.server_error'
