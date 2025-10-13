# patients/urls.py

from django.urls import path
from . import views
from .views import PatientProfileView, SaveDoctorView, MedicalRecordUploadView

# Below are basically our use cases for patients that we want to access and we do that via URLs.

urlpatterns = [
    path('profile/', PatientProfileView.as_view(), name='patient-profile'),  # view or edit patient profile
    path('fav-doctor/', SaveDoctorView.as_view(), name='save-doctor'), # save or remove favorite doctor
    path('medical-records/', MedicalRecordUploadView.as_view(), name='medical-records'), # upload or list medical records
]
