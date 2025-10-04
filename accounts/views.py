from django.shortcuts import render

# Create your views here.

# accounts/views.py

from django.http import HttpResponse

def login_view(request):
    return HttpResponse("Login Page")

def register_view(request):
    return HttpResponse("Registration Page")

def logout_view(request):
    return HttpResponse("You have been logged out.")

def dashboard_view(request):
    return HttpResponse("Welcome to your dashboard.")
