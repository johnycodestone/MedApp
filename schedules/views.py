from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone

from .models import ScheduleCategory, Schedule, ScheduleReminder
from .serializers import (
    ScheduleCategorySerializer, 
    ScheduleSerializer, 
    ScheduleReminderSerializer
)
from .permissions import (
    IsScheduleOwnerOrAdmin, 
    ScheduleReadOnly, 
    StrictScheduleAccess,
    ScheduleReminderPermission
)

class ScheduleCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Schedule Categories
    """
    queryset = ScheduleCategory.objects.all()
    serializer_class = ScheduleCategorySerializer
    permission_classes = [StrictScheduleAccess]
    
    @action(detail=True, methods=['GET'])
    def category_schedules(self, request, pk=None):
        """
        Get all schedules for a specific category
        """
        category = self.get_object()
        schedules = category.schedules.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Schedules
    """
    queryset = Schedule.objects.select_related('doctor', 'patient', 'category')
    serializer_class = ScheduleSerializer
    permission_classes = [IsScheduleOwnerOrAdmin]
    
    def get_queryset(self):
        """
        Customize queryset based on user permissions
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            doctor__user=user
        ) | self.queryset.filter(
            patient__user=user
        )
    
    @action(detail=False, methods=['GET'])
    def upcoming_schedules(self, request):
        """
        Get upcoming schedules
        """
        upcoming = self.queryset.filter(
            start_time__gt=timezone.now(),
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('start_time')[:10]
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def schedule_stats(self, request):
        """
        Get schedule statistics
        """
        total_schedules = self.queryset.count()
        status_breakdown = self.queryset.values('status').annotate(count=Count('status'))
        priority_breakdown = self.queryset.values('priority').annotate(count=Count('priority'))
        
        return Response({
            'total_schedules': total_schedules,
            'status_breakdown': list(status_breakdown),
            'priority_breakdown': list(priority_breakdown)
        })

class ScheduleReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Schedule Reminders
    """
    queryset = ScheduleReminder.objects.select_related('schedule')
    serializer_class = ScheduleReminderSerializer
    permission_classes = [ScheduleReminderPermission]
    
    def get_queryset(self):
        """
        Customize queryset based on user permissions
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            schedule__doctor__user=user
        ) | self.queryset.filter(
            schedule__patient__user=user
        )
    
    @action(detail=False, methods=['GET'])
    def unsent_reminders(self, request):
        """
        Get unsent reminders
        """
        unsent = self.queryset.filter(is_sent=False)
        serializer = self.get_serializer(unsent, many=True)
        return Response(serializer.data)

# Dashboard and Utility Views
class ScheduleDashboardView(TemplateView):
    """
    Main dashboard for schedules
    """
    template_name = 'schedules/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_schedules'] = Schedule.objects.count()
        context['upcoming_schedules'] = Schedule.objects.filter(
            start_time__gt=timezone.now(),
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('start_time')[:5]
        context['categories'] = ScheduleCategory.objects.all()
        return context

# Utility Function Views
@login_required
def schedule_calendar_view(request):
    """
    Render schedule calendar view
    """
    schedules = Schedule.objects.filter(
        Q(doctor__user=request.user) | Q(patient__user=request.user)
    )
    return render(request, 'schedules/calendar.html', {'schedules': schedules})

# Error Handler Views
def bad_request(request, exception):
    """
    Custom 400 error handler for schedules
    """
    return render(request, 'schedules/errors/400.html', status=400)

def permission_denied(request, exception):
    """
    Custom 403 error handler for schedules
    """
    return render(request, 'schedules/errors/403.html', status=403)

def page_not_found(request, exception):
    """
    Custom 404 error handler for schedules
    """
    return render(request, 'schedules/errors/404.html', status=404)

def server_error(request):
    """
    Custom 500 error handler for schedules
    """
    return render(request, 'schedules/errors/500.html', status=500)
