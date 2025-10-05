# patients/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for patients that we want to access and we do that via URLs.

urlpatterns = [
    path('profile/', views.patient_profile_view, name='patient_profile'),  # profile/ → View or edit patient profile
    path('history/', views.medical_history_view, name='medical_history'),  # history/ → View uploaded medical history
    path('dashboard/', views.patient_dashboard_view, name='patient_dashboard'),  # dashboard/ → Central hub for appointments, prescriptions, and health tips
]
