# appointments/urls.py

from django.urls import path
from . import views

app_name = 'appointments'   # 👈 this line is critical for header.html to recognize each of the apps

# Below are basically our use cases for appointments that we want to access and we do that via URLs.

urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'), # book/ → Patient books an appointment
    path('cancel/', views.cancel_appointment_view, name='cancel_appointment'), # cancel/ → Cancel an existing appointment
    path('reschedule/', views.reschedule_appointment_view, name='reschedule_appointment'), # reschedule/ → Change appointment time
    path('history/', views.appointment_history_view, name='appointment_history'), # history/ → View past and upcoming appointments
]
