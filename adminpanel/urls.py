# adminpanel/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for adminpanel that we want to access and we do that via URLs.

urlpatterns = [
    path('audit-logs/', views.audit_logs_view, name='audit_logs'), # audit-logs/ → View system activity logs
    path('assign-role/', views.assign_role_view, name='assign_role'), # assign-role/ → Assign roles to users (Doctor, Admin, etc.)
    path('backup/', views.backup_view, name='backup'), # backup/ → Trigger or view system backups
    path('version/', views.version_view, name='version_info'), # version/ → Show current system version or changelog
]
