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
from django.contrib.auth import views as auth_views

# Development-only static/media serving helpers
from django.conf import settings
from django.conf.urls.static import static

# Simple homepage view (keeps your original behavior)
def home_view(request):
    return render(request, 'pages/home.html')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

    # App routes (preserve existing order and names)
    path('doctors/', include('doctors.urls')),
     path('accounts/', include('accounts.urls')),  # intentionally commented in original
    path('adminpanel/', include('adminpanel.urls')),
    path('appointments/', include('appointments.urls')),
    path('departments/', include('departments.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('api/ml/', include('mlmodule.urls')),
    path('patients/', include('patients.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('reports/', include('reports.urls')),
    path('schedules/', include('schedules.urls')),

    # Staging page (keeps your original convenience route)
    path('staging/', TemplateView.as_view(template_name='pages/staging.html'), name='staging'),

    # Optional: DRF login/logout for the browsable API (useful during development).
    # This is safe to include and only affects the browsable API UI.
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

   
]

# Serve media (and optionally static) files during development.
# This block only runs when DEBUG is True and is safe for local testing.
if settings.DEBUG:
    # Serve user-uploaded media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Optionally serve static files from STATIC_ROOT in dev (not required if
    # STATICFILES_DIRS already covers your static assets). Uncomment if needed:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
