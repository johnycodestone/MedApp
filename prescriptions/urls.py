# prescriptions/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for prescriptions that we want to access and we do that via URLs.

urlpatterns = [
    path('create/', views.create_prescription_view, name='create_prescription'),  # create/ → Doctor issues a new prescription
    path('view/<int:prescription_id>/', views.view_prescription_view, name='view_prescription'), # view/<id>/ → Patient or pharmacist views a specific prescription
    path('download/<int:prescription_id>/', views.download_prescription_view, name='download_prescription'), # download/<id>/ → Export prescription as PDF or text
    path('history/', views.prescription_history_view, name='prescription_history'), # history/ → View all prescriptions for a patient
]
