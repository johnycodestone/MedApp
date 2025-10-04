from django.shortcuts import render

# Create your views here.

# adminpanel/views.py

from django.http import HttpResponse

def audit_logs_view(request):
    return HttpResponse("Audit Logs Page")

def assign_role_view(request):
    return HttpResponse("Role Assignment Page")

def backup_view(request):
    return HttpResponse("Backup Management Page")

def version_view(request):
    return HttpResponse("System Version Info Page")
