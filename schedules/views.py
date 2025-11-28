# schedules/views.py

# -------------------------------
# Django Core Imports
# -------------------------------
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q

# -------------------------------
# Auth and Permissions
# -------------------------------
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.permissions import IsAuthenticated

# -------------------------------
# DRF Imports
# -------------------------------
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# -------------------------------
# Local Imports
# -------------------------------
from .models import (
    ScheduleCategory, Schedule, ScheduleReminder,
    Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride
)
from doctors.models import DoctorProfile
from accounts.models import HospitalProfile
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    ScheduleCategorySerializer, ScheduleSerializer, ScheduleReminderSerializer,
    DutySerializer, ShiftSerializer, AvailabilitySlotSerializer,
    DoctorLeaveSerializer, ScheduleOverrideSerializer
)
from .permissions import (
    IsScheduleOwnerOrAdmin, StrictScheduleAccess, ScheduleReminderPermission
)

# -------------------------------
# Logging Setup
# -------------------------------
import logging
logger = logging.getLogger(__name__)

# -------------------------------
# Export Views (Placeholder)
# -------------------------------
@staff_member_required
def export_schedules_view(request):
    """
    Placeholder view to export schedules.
    Replace with actual export logic (e.g., CSV, Excel, PDF).
    """
    logger.info(f"Schedule export triggered by {request.user}")
    return JsonResponse({'message': 'Schedule export not yet implemented.'})


@staff_member_required
def export_reminders_view(request):
    """
    Placeholder view to export schedule reminders.
    Replace with actual export logic (e.g., CSV, Excel, PDF).
    """
    logger.info(f"Reminder export triggered by {request.user}")
    return JsonResponse({'message': 'Reminder export not yet implemented.'})

# -------------------------------
# Schedule Category ViewSet
# -------------------------------
class ScheduleCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing schedule categories.
    Includes custom action to fetch schedules under a category.
    """
    queryset = ScheduleCategory.objects.all()
    serializer_class = ScheduleCategorySerializer
    permission_classes = [StrictScheduleAccess]

    @action(detail=True, methods=['GET'])
    def category_schedules(self, request, pk=None):
        """
        Returns all schedules linked to a specific category.
        """
        category = self.get_object()
        schedules = category.schedules.select_related('doctor', 'patient')
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

# -------------------------------
# Schedule ViewSet
# -------------------------------
class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing schedules.
    Includes custom actions for upcoming schedules and statistics.
    """
    queryset = Schedule.objects.select_related('doctor', 'patient', 'category')
    serializer_class = ScheduleSerializer
    permission_classes = [IsScheduleOwnerOrAdmin]

    def get_queryset(self):
        """
        Filters schedules based on user role.
        Staff sees all; others see only their own.
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(doctor__user=user) | Q(patient__user=user)
        )

    @action(detail=False, methods=['GET'])
    def upcoming_schedules(self, request):
        """
        Returns next 10 upcoming schedules.
        """
        upcoming = self.get_queryset().filter(
            start_time__gt=timezone.now(),
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('start_time')[:10]
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def schedule_stats(self, request):
        """
        Returns statistics on schedule status and priority.
        """
        qs = self.get_queryset()
        return Response({
            'total_schedules': qs.count(),
            'status_breakdown': list(qs.values('status').annotate(count=Count('status'))),
            'priority_breakdown': list(qs.values('priority').annotate(count=Count('priority')))
        })

# -------------------------------
# Schedule Reminder ViewSet
# -------------------------------
class ScheduleReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing schedule reminders.
    Includes custom action to fetch unsent reminders.
    """
    queryset = ScheduleReminder.objects.select_related('schedule')
    serializer_class = ScheduleReminderSerializer
    permission_classes = [ScheduleReminderPermission]

    def get_queryset(self):
        """
        Filters reminders based on user role.
        Staff sees all; others see only their own.
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(schedule__doctor__user=user) | Q(schedule__patient__user=user)
        )

    @action(detail=False, methods=['GET'])
    def unsent_reminders(self, request):
        """
        Returns reminders that haven't been sent yet.
        """
        unsent = self.get_queryset().filter(is_sent=False)
        serializer = self.get_serializer(unsent, many=True)
        return Response(serializer.data)

# -------------------------------
# Duty ViewSet
# -------------------------------
class DutyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing hospital duty assignments.
    """
    queryset = Duty.objects.select_related('doctor', 'hospital', 'department')
    serializer_class = DutySerializer
    permission_classes = [IsAuthenticated]

# -------------------------------
# Shift ViewSet
# -------------------------------
class ShiftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shifts under duties.
    """
    queryset = Shift.objects.select_related('duty', 'duty__doctor')
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

# -------------------------------
# Availability Slot ViewSet
# -------------------------------
class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing availability slots within shifts.
    """
    queryset = AvailabilitySlot.objects.select_related('shift', 'booked_by')
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]

# -------------------------------
# Doctor Leave ViewSet
# -------------------------------
class DoctorLeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor leave requests.
    """
    queryset = DoctorLeave.objects.select_related('doctor', 'approved_by')
    serializer_class = DoctorLeaveSerializer
    permission_classes = [IsAuthenticated]

# -------------------------------
# Schedule Override ViewSet
# -------------------------------
class ScheduleOverrideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing manual schedule overrides.
    """
    queryset = ScheduleOverride.objects.select_related('doctor', 'created_by')
    serializer_class = ScheduleOverrideSerializer
    permission_classes = [IsAuthenticated]

# -------------------------------
# Dashboard View
# -------------------------------
class ScheduleDashboardView(TemplateView):
    """
    Renders the main dashboard for schedules.
    Shows total schedules, upcoming ones, and categories.
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

# -------------------------------
# Calendar View
# -------------------------------
@login_required
def schedule_calendar_view(request):
    """
    Renders the calendar view for a user's schedules.
    """
    schedules = Schedule.objects.filter(
        Q(doctor__user=request.user) | Q(patient__user=request.user)
    )
    return render(request, 'schedules/calendar.html', {'schedules': schedules})

# -------------------------------
# Doctor Schedules View
# -------------------------------
@login_required
def doctor_schedules_view(request):
    """
    Renders the doctor schedules page showing:
    - Doctor's duties, shifts, availability slots
    - Doctor's leaves and overrides
    - Upcoming schedules
    """
    # Get doctor profile - ensure it's a DoctorProfile instance
    doctor_profile = None
    if hasattr(request.user, 'doctors_doctor_profile'):
        try:
            profile = request.user.doctors_doctor_profile
            # Ensure it's actually a DoctorProfile instance, not a string or other type
            if isinstance(profile, DoctorProfile):
                doctor_profile = profile
        except (DoctorProfile.DoesNotExist, ObjectDoesNotExist, AttributeError):
            pass
    
    if not doctor_profile:
        # If user is not a doctor, show empty state or redirect
        context = {
            'doctor_profile': None,
            'duties': [],
            'shifts': [],
            'availability_slots': [],
            'leaves': [],
            'overrides': [],
            'upcoming_schedules': [],
            'crumbs': [
                {"label": "Home", "url": "/"},
                {"label": "Schedules", "url": "/schedules/"},
                {"label": "Doctor Schedules", "url": None},
            ],
        }
        return render(request, 'schedules/doctor_schedules.html', context)
    
    # Get all duties for this doctor - use doctor_profile.id to ensure we're using the ID
    duties = Duty.objects.filter(doctor_id=doctor_profile.id).select_related('hospital', 'department').order_by('-start_date')
    
    # Get all shifts for these duties - use doctor_id to ensure we're using the ID
    shifts = Shift.objects.filter(duty__doctor_id=doctor_profile.id).select_related('duty', 'duty__hospital').order_by('day_of_week', 'start_time')
    
    # Get availability slots (upcoming ones)
    today = timezone.now().date()
    availability_slots = AvailabilitySlot.objects.filter(
        shift__duty__doctor_id=doctor_profile.id,
        date__gte=today
    ).select_related('shift', 'shift__duty', 'booked_by').order_by('date', 'start_time')[:50]
    
    # Get doctor leaves - use doctor_id
    leaves = DoctorLeave.objects.filter(doctor_id=doctor_profile.id).order_by('-start_date')
    
    # Get schedule overrides - use doctor_id
    overrides = ScheduleOverride.objects.filter(doctor_id=doctor_profile.id).order_by('-date')
    
    # Get upcoming schedules - use doctor_id
    upcoming_schedules = Schedule.objects.filter(
        doctor_id=doctor_profile.id,
        start_time__gte=timezone.now()
    ).select_related('patient', 'category').order_by('start_time')[:10]
    
    context = {
        'doctor_profile': doctor_profile,
        'duties': duties,
        'shifts': shifts,
        'availability_slots': availability_slots,
        'leaves': leaves,
        'overrides': overrides,
        'upcoming_schedules': upcoming_schedules,
        'crumbs': [
            {"label": "Home", "url": "/"},
            {"label": "Schedules", "url": "/schedules/"},
            {"label": "Doctor Schedules", "url": None},
        ],
    }
    return render(request, 'schedules/doctor_schedules.html', context)

# -------------------------------
# Hospital Schedules View
# -------------------------------
@login_required
def hospital_schedules_view(request):
    """
    Renders the hospital schedules page showing:
    - Hospital-assigned duties to doctors
    - Shifts within duties
    - Related schedules
    """
    # Get hospital profile - ensure it's a HospitalProfile instance
    hospital_profile = None
    if hasattr(request.user, 'accounts_hospital_profile'):
        try:
            profile = request.user.accounts_hospital_profile
            # Ensure it's actually a HospitalProfile instance, not a string or other type
            if isinstance(profile, HospitalProfile):
                hospital_profile = profile
        except (HospitalProfile.DoesNotExist, ObjectDoesNotExist, AttributeError):
            pass
    
    if not hospital_profile:
        # If user is not a hospital, show empty state
        context = {
            'hospital_profile': None,
            'duties': [],
            'shifts': [],
            'related_schedules': [],
            'crumbs': [
                {"label": "Home", "url": "/"},
                {"label": "Schedules", "url": "/schedules/"},
                {"label": "Hospital Schedules", "url": None},
            ],
        }
        return render(request, 'schedules/hospital_schedules.html', context)
    
    # Get all duties assigned by this hospital - use hospital_id to ensure we're using the ID
    duties = Duty.objects.filter(hospital_id=hospital_profile.id).select_related('doctor', 'department').order_by('-start_date')
    
    # Get all shifts for these duties - use hospital_id
    shifts = Shift.objects.filter(duty__hospital_id=hospital_profile.id).select_related('duty', 'duty__doctor', 'duty__department').order_by('duty__start_date', 'day_of_week', 'start_time')
    
    # Get related schedules (schedules for doctors with duties at this hospital)
    doctor_ids = duties.values_list('doctor_id', flat=True).distinct()
    related_schedules = Schedule.objects.filter(
        doctor_id__in=doctor_ids,
        start_time__gte=timezone.now()
    ).select_related('doctor', 'patient', 'category').order_by('start_time')[:20]
    
    # Get unique doctor count
    unique_doctors_count = duties.values('doctor').distinct().count()
    
    context = {
        'hospital_profile': hospital_profile,
        'duties': duties,
        'shifts': shifts,
        'related_schedules': related_schedules,
        'unique_doctors_count': unique_doctors_count,
        'crumbs': [
            {"label": "Home", "url": "/"},
            {"label": "Schedules", "url": "/schedules/"},
            {"label": "Hospital Schedules", "url": None},
        ],
    }
    return render(request, 'schedules/hospital_schedules.html', context)

# -------------------------------
# Error Handler Views
# -------------------------------
def bad_request(request, exception):
    """
    Custom 400 error handler.
    """
    return render(request, 'schedules/errors/400.html', status=400)

def permission_denied(request, exception):
    """
    Custom 403 error handler.
    """
    return render(request, 'schedules/errors/403.html', status=403)

def page_not_found(request, exception):
    """
    Custom 404 error handler.
    """
    return render(request, 'schedules/errors/404.html', status=404)

def server_error(request):
    """
    Custom 500 error handler.
    """
    return render(request, 'schedules/errors/500.html', status=500)
