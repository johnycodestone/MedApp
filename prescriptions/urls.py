from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    path('', views.prescription_list, name='list'),
    path('create/', views.create_prescription, name='create'),
]
