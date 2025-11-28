"""
URL configuration for medapp_core project.

This file preserves your existing routes and adds a couple of safe, optional
development conveniences:
- Serves MEDIA files in DEBUG mode (useful for local testing).
- Optionally exposes DRF's login views for the browsable API (api-auth).
All existing app includes and the simple home_view are left intact.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView

# Development-only static/media serving helpers
from django.conf import settings
from django.conf.urls.static import static


# Simple homepage view (keeps your original behavior)
def home_view(request):
    return render(request, 'pages/home.html')


urlpatterns = [
    # -------------------------------
    # Core + Admin
    # -------------------------------
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    # -------------------------------
    # App routes (frontend + modules)
    # -------------------------------
    path('accounts/', include(('django.contrib.auth.urls', 'accounts'), namespace='accounts')),
    path('doctors/', include(('doctors.urls', 'doctors'), namespace='doctors')),
    # path('accounts/', include('accounts.urls')),  # intentionally commented in original
    path('adminpanel/', include(('adminpanel.urls', 'adminpanel'), namespace='adminpanel')),
    path('appointments/', include(('appointments.urls', 'appointments'), namespace='appointments')),
    path('departments/', include(('departments.urls', 'departments'), namespace='departments')),
    path('hospitals/', include(('hospitals.urls', 'hospitals'), namespace='hospitals')),
    path('api/ml/', include(('mlmodule.urls', 'mlmodule'), namespace='mlmodule')),
    path('patients/', include(('patients.urls', 'patients'), namespace='patients')),
    path('prescriptions/', include(('prescriptions.urls', 'prescriptions'), namespace='prescriptions')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('schedules/', include(('schedules.urls', 'schedules'), namespace='schedules')),

    # -------------------------------
    # Utility + Staging
    # -------------------------------
    path('staging/', TemplateView.as_view(template_name='pages/staging.html'), name='staging'),

    # -------------------------------
    # DRF Browsable API login/logout
    # -------------------------------
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]


# -------------------------------
# Development-only static/media serving
# -------------------------------
if settings.DEBUG:
    # Serve user-uploaded media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Optionally serve static files from STATIC_ROOT in dev
    # Uncomment if needed:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
