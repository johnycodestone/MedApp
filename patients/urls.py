from django.urls import path
from . import views
from .views import (
    PatientProfileView,
    SaveDoctorView,
    MedicalRecordUploadView,
    staging_view,
    dashboard_view,
    profile_page_view,
    history_view
)

app_name = 'patients'

urlpatterns = [
    # UI Routes
    path('', dashboard_view, name='dashboard'),
    path('profile/', PatientProfileView.as_view(), name='profile'),  # ✅ renamed
    path('history/', history_view, name='history'),
    path('profile-page/', profile_page_view, name='profile-page'),
    path("urgency/", views.urgency_predict_view, name="urgency"),
    path("diabetes/", views.diabetes_predict_view, name="diabetes"),
    # API Routes
    path('profile/<int:pk>/', PatientProfileView.as_view(), name='detail'),
    path('fav-doctor/', SaveDoctorView.as_view(), name='save-doctor'),
    path('medical-records/', MedicalRecordUploadView.as_view(), name='medical-records'),
    path('staging/', staging_view, name='staging'),

]
