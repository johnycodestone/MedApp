from django.shortcuts import render

# Create your views here.

# hospitals/views.py

from django.http import HttpResponse

def create_hospital_view(request):
    return HttpResponse("Create Hospital Page")

def list_hospitals_view(request):
    return HttpResponse("List of Hospitals")

def update_hospital_view(request, hospital_id):
    return HttpResponse(f"Update Hospital {hospital_id}")

def delete_hospital_view(request, hospital_id):
    return HttpResponse(f"Delete Hospital {hospital_id}")

def assign_duty_view(request, hospital_id):
    return HttpResponse(f"Assign Duty for Hospital {hospital_id}")

