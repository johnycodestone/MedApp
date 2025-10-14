## doctors/urls.py
#
#from django.urls import path
#from . import views
#
## Below are basically our use cases for doctors that we want to access and we do that via URLs.
#
#urlpatterns = [
#    path('profile/', views.doctor_profile, name='doctor_profile'),
#    path('availability/', views.doctor_availability, name='doctor_availability'),
#]

from django.urls import path
from .views import DoctorProfileView, TimetableView, CancelAppointmentView, PrescriptionView

urlpatterns = [
    path("profile/", DoctorProfileView.as_view(), name="doctor-profile"),
    path("timetable/", TimetableView.as_view(), name="doctor-timetable"),
    path("cancel-appointment/", CancelAppointmentView.as_view(), name="cancel-appointment"),
    path("prescriptions/", PrescriptionView.as_view(), name="doctor-prescriptions"),
]
