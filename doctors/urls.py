# doctors/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for doctors that we want to access and we do that via URLs.

urlpatterns = [
    path('profile/', views.doctor_profile, name='doctor_profile'),
    path('availability/', views.doctor_availability, name='doctor_availability'),
]
