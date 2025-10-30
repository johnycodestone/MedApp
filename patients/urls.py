# patients/urls.py

from django.urls import path
from . import views
from .views import PatientProfileView, SaveDoctorView, MedicalRecordUploadView, staging_view

app_name = 'patients'   # 👈 this line is critical for header.html to recognize each of the apps

# Below are basically our use cases for patients that we want to access and we do that via URLs.

'''urlpatterns = [
    path('profile/', PatientProfileView.as_view(), name='patient-profile'),  # view or edit patient profile
    path('fav-doctor/', SaveDoctorView.as_view(), name='save-doctor'), # save or remove favorite doctor
    path('medical-records/', MedicalRecordUploadView.as_view(), name='medical-records'), # upload or list medical records
    path('staging/', staging_view, name='staging'),  # Added by Waqar to render the staging.html template
]'''

urlpatterns = [
    # UI Routes
    path('', views.patient_list_view, name='list'),  # ✅ Add this
    path('profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('profile/<int:pk>/', PatientProfileView.as_view(), name='detail'),
    path('fav-doctor/', SaveDoctorView.as_view(), name='save-doctor'),
    path('medical-records/', MedicalRecordUploadView.as_view(), name='medical-records'),
    path('staging/', staging_view, name='staging'),
]
