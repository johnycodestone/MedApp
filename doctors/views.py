# doctors/views.py
"""
Existing views preserved. New DoctorDashboardView appended at the end.
- All original API and HTML views are left unchanged.
- New dashboard view is additive and uses presenters + services.
- SOLID:
  - SRP: existing views keep their responsibilities.
  - DIP: new view depends on services/presenters abstractions.
- Patterns:
  - Template Method (conceptual): dashboard view orchestrates steps and delegates mapping.
"""

from django.views.generic import ListView
from django.db.models import Q
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from datetime import timedelta, datetime

from .models import DoctorProfile, SPECIALIZATION_CHOICES
from .serializers import DoctorProfileSerializer, TimetableSerializer, PrescriptionSerializer
from appointments.models import Appointment, AppointmentStatus
from prescriptions.models import Prescription   # ✅ unified Prescription model
from .services import (
    ensure_doctor_profile, manage_timetable, get_timetable,
    cancel_patient_appointment
)

# ---------------------------
# Section A: API Views
# ---------------------------

class DoctorProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = ensure_doctor_profile(request.user)
        return Response(DoctorProfileSerializer(profile).data)


class TimetableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES["file"]
        timetable = manage_timetable(request.user, file_obj)
        return Response(TimetableSerializer(timetable).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        tt = get_timetable(request.user)
        return Response(TimetableSerializer(tt).data if tt else {}, status=status.HTTP_200_OK)


class CancelAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        reason = request.data.get("reason", "")
        cancel_patient_appointment(request.user, appointment_id, reason)
        return Response({"status": "Appointment cancelled"}, status=status.HTTP_200_OK)


class PrescriptionView(APIView):
    """
    API for creating and listing prescriptions tied to appointments.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        pdf = request.FILES.get("pdf_file")

        # ✅ prescriptions are tied to appointments, not directly to patients
        appointment_id = data.get("appointment_id")
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)

        pres = Prescription.objects.create(
            appointment=appointment,
            notes=data.get("text", "")
        )
        if pdf:
            pres.pdf_file = pdf
            pres.save()

        return Response(PrescriptionSerializer(pres).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        prescriptions = Prescription.objects.filter(appointment__doctor__user=request.user)
        return Response(PrescriptionSerializer(prescriptions, many=True).data)


# ---------------------------
# Section B: Frontend HTML Views
# ---------------------------

class DoctorListView(ListView):
    """
    HTML page: Doctors list with filters and pagination.
    """
    model = DoctorProfile
    context_object_name = "doctors"
    template_name = "doctors/doctor_list.html"
    paginate_by = 10

    def get_queryset(self):
        qs = DoctorProfile.objects.select_related("user").all()
        params = self.request.GET

        # Text search: name, bio, qualification
        q = (params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(bio__icontains=q) |
                Q(qualification__icontains=q)
            )

        # Specialization filter
        specialization = (params.get("specialization") or "").strip()
        if specialization:
            qs = qs.filter(specialization=specialization)

        # Minimum experience filter
        min_exp_raw = (params.get("min_exp") or "").strip()
        if min_exp_raw.isdigit():
            qs = qs.filter(experience_years__gte=int(min_exp_raw))

        # Minimum rating filter
        min_rating_raw = (params.get("min_rating") or "").strip()
        try:
            if min_rating_raw:
                qs = qs.filter(rating__gte=float(min_rating_raw))
        except ValueError:
            pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()

        ctx["filters"] = {
            "q": params.get("q", ""),
            "specialization": params.get("specialization", ""),
            "min_exp": params.get("min_exp", ""),
            "min_rating": params.get("min_rating", ""),
        }
        ctx["specializations"] = SPECIALIZATION_CHOICES
        ctx["crumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": "Doctors", "url": None},
        ]
        return ctx


User = get_user_model()

class DoctorDetailView(View):
    """
    HTML page: Doctor detail with available slots for booking.
    """
    def get(self, request, id):
        doctor = get_object_or_404(User, id=id)
        profile = getattr(doctor, "doctors_doctor_profile", None)

        today = timezone.now()
        next_week = today + timedelta(days=7)

        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__range=(today, next_week),
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).values_list("scheduled_time", flat=True)

        slots = []
        for day in range(7):
            date = today + timedelta(days=day)
            for hour in range(9, 17):
                slot_time = timezone.make_aware(
                    datetime(date.year, date.month, date.day, hour),
                    timezone.get_current_timezone()
                )
                if slot_time not in booked_slots:
                    slots.append(slot_time)

        context = {
            "doctor": doctor,
            "profile": profile,
            "available_slots": slots,
            "crumbs": [
                {"label": "Home", "url": "/"},
                {"label": "Doctors", "url": "/doctors/"},
                {"label": f"Dr. {doctor.get_full_name()}", "url": None},
            ],
        }
        return render(request, "doctors/doctor_detail.html", context)


# ---------------------------
# Section C: New - Doctor Dashboard (additive)
# ---------------------------

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Import presenters and dashboard helpers (added modules)
from . import presenters
from . import services as dashboard_services

class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    """
    Doctor user account dashboard.
    - Non-destructive addition: does not modify existing views.
    - Orchestrates data retrieval via services and mapping via presenters.
    - SOLID:
      - SRP: view only orchestrates; presenters/services handle mapping and data access.
      - DIP: view depends on service/presenter abstractions.
    - Patterns:
      - Template Method (conceptual): get_context_data defines the skeleton.
      - Factory/Adapter: presenters.build_action and adapters used to create template-ready dicts.
    """
    template_name = "doctors/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Breadcrumbs
        ctx["crumbs"] = [
            {"label": "Home", "href": "/"},
            {"label": "Doctors", "href": "/doctors/"},
            {"label": "Dashboard", "href": None},
        ]

        # Build quick actions using presenters (factory). If reverse fails, href will be None.
        ctx["actions"] = [
            presenters.build_action("My Appointments", icon="📅", url_name="appointments:appointment-list", variant="primary"),
            presenters.build_action("My Patients", icon="🧑‍⚕️", url_name="patients:list", variant="success"),
            presenters.build_action("My Shifts", icon="🕒", url_name="shifts:list", variant="info"),
            presenters.build_action("My Reports", icon="📊", url_name="reports:dashboard", variant="secondary"),
        ]

        # KPIs: use dashboard_services which are additive and safe
        try:
            ctx["kpis"] = [
                {"label": "Today Appointments", "value": dashboard_services.count_todays_appointments(self.request.user), "icon": "📅"},
                {"label": "On-Call Now", "value": dashboard_services.count_current_oncall(self.request.user), "icon": "🕒"},
                {"label": "Active Patients", "value": dashboard_services.count_active_patients(self.request.user), "icon": "🧑‍⚕️"},
            ]
        except Exception:
            # Fail-safe: if services are not available or error occurs, provide safe defaults
            ctx["kpis"] = [
                {"label": "Today Appointments", "value": 0, "icon": "📅"},
                {"label": "On-Call Now", "value": 0, "icon": "🕒"},
                {"label": "Active Patients", "value": 0, "icon": "🧑‍⚕️"},
            ]

        # Summaries: fetch via services and adapt via presenters
        try:
            appts = dashboard_services.get_upcoming_appointments_for_doctor(self.request.user)
            ctx["appointments"] = [presenters.appointment_adapter(a) for a in appts]
        except Exception:
            ctx["appointments"] = []

        try:
            shifts = dashboard_services.get_upcoming_shifts_for_doctor(self.request.user)
            ctx["shifts"] = [presenters.shift_adapter(s) for s in shifts]
        except Exception:
            ctx["shifts"] = []

        try:
            patients = dashboard_services.get_active_patients_for_doctor(self.request.user)
            ctx["patients"] = [presenters.patient_adapter(p) for p in patients]
        except Exception:
            ctx["patients"] = []

        try:
            reports = dashboard_services.get_recent_reports_for_doctor(self.request.user)
            ctx["reports"] = [presenters.report_adapter(r) for r in reports]
        except Exception:
            ctx["reports"] = []

        return ctx
