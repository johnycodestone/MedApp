"""
URL configuration for medapp_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

# Simple homepage view added by Waqar
def home_view(request):
    return render(request, 'pages/home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Simple homepage view added by Waqar
    path('doctors/', include('doctors.urls')),
    #path('accounts/', include('accounts.urls')),
    path('adminpanel/', include('adminpanel.urls')),
    path('appointments/', include('appointments.urls')),
    path('departments/', include('departments.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('api/ml/', include('mlmodule.urls')),
    path('patients/', include('patients.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('reports/', include('reports.urls')),
    path('schedules/', include('schedules.urls')),
]
