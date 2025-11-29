# hospitals/views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from .models import Hospital
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse, NoReverseMatch

def build_action(label, icon=None, url_name=None, url_arg=None, variant=None, aria_label=None, href=None):
    """
    Build a robust quick action dict. Prefer resolving URL names to href in Python.
    If reverse fails, leaves href as None so the template renders a disabled button.
    """
    if href is None and url_name:
        try:
            href = reverse(url_name, args=[url_arg]) if url_arg is not None else reverse(url_name)
        except NoReverseMatch:
            href = None  # Template will gracefully render a disabled button
    return {
        "label": label,
        "icon": icon,
        "variant": variant,
        "aria_label": aria_label or label,
        "href": href,
    }

# -------------------------------------------------------------------
# Basic CRUD stubs (can be expanded later)
# -------------------------------------------------------------------

def create_hospital_view(request):
    return HttpResponse("Create Hospital Page")

def list_hospitals_view(request):
    return HttpResponse("List of Hospitals")

def update_hospital_view(request, hospital_id):
    return HttpResponse(f"Update Hospital {hospital_id}")

def delete_hospital_view(request, hospital_id):
    return HttpResponse(f"Delete Hospital {hospital_id}")

def assign_duty_view(request, hospital_id):
    return HttpResponse(f"Assign Duty for Hospital {hospital_id}")

# -------------------------------------------------------------------
# REST API endpoints (using DRF)
# -------------------------------------------------------------------

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import register_hospital, manage_department, manage_doctor, get_reports
from .serializers import (
    HospitalSerializer,
    DepartmentSerializer,
    DoctorAssignmentSerializer,
    ReportSerializer,
)

class HospitalProfileView(APIView):
    """
    API endpoint to register a hospital profile for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        hospital = register_hospital(
            request.user,
            data.get("name"),
            address=data.get("address"),
            phone=data.get("phone")
        )
        return Response(HospitalSerializer(hospital).data, status=status.HTTP_201_CREATED)


class DepartmentView(APIView):
    """
    API endpoint to manage hospital departments (add/remove).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        dept = manage_department(
            request.user.hospital_profile,
            "add",
            data["name"],
            data.get("description", "")
        )
        return Response(DepartmentSerializer(dept).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        data = request.data
        manage_department(request.user.hospital_profile, "remove", data["name"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DoctorDutyView(APIView):
    """
    API endpoint to assign or waive doctor duties in a hospital.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        assign = manage_doctor(
            request.user.hospital_profile,
            data["doctor_id"],
            "assign",
            data.get("department")
        )
        return Response(DoctorAssignmentSerializer(assign).data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        data = request.data
        manage_doctor(request.user.hospital_profile, data["doctor_id"], "waive")
        return Response({"status": "Duty Waived"}, status=status.HTTP_200_OK)


class ReportListView(APIView):
    """
    API endpoint to list hospital reports for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reports = get_reports(request.user.hospital_profile)
        return Response(ReportSerializer(reports, many=True).data)

# -------------------------------------------------------------------
# Frontend views (List + Detail pages)
# -------------------------------------------------------------------

class HospitalsListPageView(ListView):
    """
    Hospitals list view
    - Renders hospitals_list.html
    - Provides hospitals queryset with badges and KPIs precomputed
    - Adds crumbs, filters, and search toggle to context
    """
    model = Hospital
    template_name = "hospitals/hospitals_list.html"
    context_object_name = "hospitals"
    paginate_by = 12  # adjust as needed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Precompute badges and KPIs for each hospital
        for h in context["hospitals"]:
            # Badges
            h.badges = []
            if h.is_verified:
                h.badges.append({"label": "PMC Verified", "variant": "success"})

            # KPIs
            h.kpis = []
            if h.beds_total:
                h.kpis.append({
                    "label": "Beds",
                    "value": f"{h.beds_available}/{h.beds_total}"
                })
            if h.specialties_count:
                h.kpis.append({
                    "label": "Specialties",
                    "value": h.specialties_count
                })

        # Example crumbs and filters; replace with real logic later
        context["crumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": "Hospitals", "url": "/hospitals/"}
        ]
        context["filters"] = []
        context["show_search"] = True
        return context


class HospitalsDetailPageView(DetailView):
    """
    Hospital detail view
    - Renders hospitals_detail.html
    - Provides hospital object plus stats, crumbs, and related departments
    """
    model = Hospital
    template_name = "hospitals/hospitals_detail.html"
    context_object_name = "hospital"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hospital = self.get_object()

        # Stats block for detail page
        context["stats"] = [
            {"label": "Beds", "value": f"{hospital.beds_available}/{hospital.beds_total}", "icon": "🛏️"},
            {"label": "Specialties", "value": hospital.specialties_count, "icon": "⚕️"},
        ]

        # Breadcrumbs
        context["crumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": "Hospitals", "url": "/hospitals/"},
            {"label": hospital.name, "url": f"/hospitals/{hospital.id}/"},
        ]

        # Related departments (if any)
        context["departments"] = getattr(hospital, "departments", None)
        return context


class HospitalDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "hospitals/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "crumbs": [
                {"label": "Home", "href": "/"},
                {"label": "Hospitals", "href": "/hospitals/"},
                {"label": "Dashboard", "href": None},
            ],
            "actions": [
                {"label": "Manage Appointments", "icon": "📅", "url_name": "appointments:appointment-list", "variant": "primary"},
                {"label": "Manage Doctors", "icon": "⚕️", "url_name": "doctors:doctor-list", "variant": "primary"},
                {"label": "Manage Departments", "icon": "🏥", "url_name": "departments:page-list"},
                {"label": "View Reports", "icon": "📊", "url_name": "reports:dashboard"},
            ],
            "kpis": [
                {"label": "Beds Available", "value": "34", "icon": "🛏️", "trend": "+2"},
                {"label": "Occupancy", "value": "78%", "icon": "📈", "hint": "Goal: < 85%"},
                {"label": "Admissions Today", "value": "12", "icon": "🧾"},
            ],
            "appointments": [],
            "doctors": [],
            "departments": [],
            "reports": [],
        })
        return ctx