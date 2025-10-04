# reports/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for reports that we want to access and we do that via URLs.

urlpatterns = [
    path('analytics/', views.analytics_report_view, name='analytics_report'), # analytics/ → Visual insights (appointments, prescriptions, patient load)
    path('usage/', views.usage_report_view, name='usage_report'), # usage/ → System usage metrics (logins, activity, traffic)
    path('export/', views.export_report_view, name='export_report'), # export/ → Download reports (CSV, PDF, etc.)
]
