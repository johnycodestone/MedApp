from django.shortcuts import render

# Create your views here.

# reports/views.py

from django.http import HttpResponse

def analytics_report_view(request):
    return HttpResponse("Analytics Report Page")

def usage_report_view(request):
    return HttpResponse("System Usage Report Page")

def export_report_view(request):
    return HttpResponse("Export Report Page")

