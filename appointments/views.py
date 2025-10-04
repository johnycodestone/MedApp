from django.shortcuts import render

# Create your views here.

# appointments/views.py

from django.http import HttpResponse

def book_appointment_view(request):
    return HttpResponse("Book Appointment Page")

def cancel_appointment_view(request):
    return HttpResponse("Cancel Appointment Page")

def reschedule_appointment_view(request):
    return HttpResponse("Reschedule Appointment Page")

def appointment_history_view(request):
    return HttpResponse("Appointment History Page")
