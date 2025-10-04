from django.shortcuts import render

# Create your views here.

# schedules/views.py

from django.http import HttpResponse

def create_schedule_view(request):
    return HttpResponse("Create Schedule Page")

def list_schedules_view(request):
    return HttpResponse("List of Schedules")

def update_schedule_view(request, schedule_id):
    return HttpResponse(f"Update Schedule {schedule_id}")

def delete_schedule_view(request, schedule_id):
    return HttpResponse(f"Delete Schedule {schedule_id}")
