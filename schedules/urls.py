# schedules/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ScheduleCategoryViewSet,
    ScheduleViewSet,
    ScheduleReminderViewSet,
    ScheduleDashboardView,
    schedule_calendar_view
)


app_name = 'schedules'

# Create a router for API viewsets
router = DefaultRouter()
router.register(r'categories', ScheduleCategoryViewSet, basename='schedule-category')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'reminders', ScheduleReminderViewSet, basename='schedule-reminder')

urlpatterns = [
    # Dashboard and Main Views
    path('', ScheduleDashboardView.as_view(), name='schedule-dashboard'),
    path('calendar/', schedule_calendar_view, name='schedule-calendar'),
    
    # API Routes
    path('api/', include(router.urls)),
    
    # Additional Schedule-specific routes
    path('api/stats/', include([
        path('category-schedules/<int:pk>/', 
             ScheduleCategoryViewSet.as_view({'get': 'category_schedules'}), 
             name='category-schedules'),
        path('upcoming/', 
             ScheduleViewSet.as_view({'get': 'upcoming_schedules'}), 
             name='upcoming-schedules'),
        path('schedule-summary/', 
             ScheduleViewSet.as_view({'get': 'schedule_stats'}), 
             name='schedule-stats'),
        path('unsent-reminders/', 
             ScheduleReminderViewSet.as_view({'get': 'unsent_reminders'}), 
             name='unsent-reminders'),
    ])),
    
    # Utility Routes
    path('export/', include([
        path('schedules/', views.export_schedules_view, name='export-schedules'),
        path('reminders/', views.export_reminders_view, name='export-reminders'),
    ]))
]

# Optional: Custom error handlers for schedule views
handler400 = 'schedules.views.bad_request'
handler403 = 'schedules.views.permission_denied'
handler404 = 'schedules.views.page_not_found'
handler500 = 'schedules.views.server_error'
