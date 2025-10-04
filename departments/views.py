from django.shortcuts import render

# Create your views here.

# departments/views.py

from django.http import HttpResponse

def create_department_view(request):
    return HttpResponse("Create Department Page")

def list_departments_view(request):
    return HttpResponse("List of Departments")

def update_department_view(request, dept_id):
    return HttpResponse(f"Update Department {dept_id}")

def delete_department_view(request, dept_id):
    return HttpResponse(f"Delete Department {dept_id}")
