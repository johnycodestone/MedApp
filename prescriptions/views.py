from django.shortcuts import render

# Create your views here.

# prescriptions/views.py

from django.http import HttpResponse

def create_prescription_view(request):
    return HttpResponse("Create Prescription Page")

def view_prescription_view(request, prescription_id):
    return HttpResponse(f"Viewing Prescription {prescription_id}")

def download_prescription_view(request, prescription_id):
    return HttpResponse(f"Download Prescription {prescription_id}")

def prescription_history_view(request):
    return HttpResponse("Prescription History Page")
