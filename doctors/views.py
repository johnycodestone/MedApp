from django.shortcuts import render

# Create your views here.

# doctors/views.py

from django.http import HttpResponse

def doctor_profile(request):
    return HttpResponse("Doctor Profile Page")

def doctor_availability(request):
    return HttpResponse("Doctor Availability Page")
