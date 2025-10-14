# adminpanel/urls.py

from django.urls import path, include
from django.contrib.admin import site
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    PatientViewSet,
    DoctorViewSet,
    AppointmentViewSet,
    MedicalRecordViewSet,
    PrescriptionViewSet,
    AdminDashboardView
)

# Create a router for API viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    # Django Admin Site
    path('django-admin/', site.urls, name='django-admin'),
    
    # Admin Dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # API Routes
    path('api/', include(router.urls)),
    
    # Additional Admin-specific routes
    path('api/stats/', include([
        path('patient-count/', views.patient_count_view, name='patient-count'),
        path('appointment-stats/', views.appointment_stats_view, name='appointment-stats'),
        path('revenue-summary/', views.revenue_summary_view, name='revenue-summary'),
    ])),
    
    # Authentication Routes
    path('api/auth/', include([
        path('login/', views.admin_login_view, name='admin-login'),
        path('logout/', views.admin_logout_view, name='admin-logout'),
        path('password-reset/', views.admin_password_reset_view, name='admin-password-reset'),
    ]))
]

# Optional: Custom error handlers for admin views
handler400 = 'adminpanel.views.bad_request'
handler403 = 'adminpanel.views.permission_denied'
handler404 = 'adminpanel.views.page_not_found'
handler500 = 'adminpanel.views.server_error'
