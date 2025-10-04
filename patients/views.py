from django.shortcuts import render

# Create your views here.

# patients/views.py

from django.http import HttpResponse

def patient_profile_view(request):
    return HttpResponse("Patient Profile Page")

def medical_history_view(request):
    return HttpResponse("Medical History Page")

def patient_dashboard_view(request):
    return HttpResponse("Patient Dashboard")
