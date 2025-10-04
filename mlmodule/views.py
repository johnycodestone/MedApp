from django.shortcuts import render

# Create your views here.

# mlmodule/views.py

from django.http import HttpResponse

def urgency_triage_view(request):
    return HttpResponse("Urgency Triage Prediction Page")

def diabetes_prediction_view(request):
    return HttpResponse("Diabetes Prediction Page")

def health_tips_view(request):
    return HttpResponse("Health Tips and Awareness Content")
