#from django.shortcuts import render
#
## Create your views here.
#
## doctors/views.py
#
#from django.http import HttpResponse
#
#def doctor_profile(request):
#    return HttpResponse("Doctor Profile Page")
#
#def doctor_availability(request):
#    return HttpResponse("Doctor Availability Page")

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import DoctorProfileSerializer, TimetableSerializer, PrescriptionSerializer
from django.views.generic import ListView
from django.db.models import Q
from .models import DoctorProfile
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from appointments.models import Appointment, AppointmentStatus
from datetime import datetime, timedelta
from .services import (
    ensure_doctor_profile, manage_timetable, get_timetable,
    cancel_patient_appointment, give_prescription, get_doctor_prescriptions
)

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
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        pdf = request.FILES.get("pdf_file")
        pres = give_prescription(request.user, data["patient_id"], data["text"], pdf)
        return Response(PrescriptionSerializer(pres).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        prescriptions = get_doctor_prescriptions(request.user)
        return Response(PrescriptionSerializer(prescriptions, many=True).data)



class DoctorListView(ListView):
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 12  # adjust if your components expect different

    def get_queryset(self):
        qs = DoctorProfile.objects.select_related("user").all()

        # Basic filters aligned with your model
        q = self.request.GET.get("q", "").strip()
        specialization = self.request.GET.get("specialization", "").strip()
        min_exp = self.request.GET.get("min_exp", "").strip()
        min_rating = self.request.GET.get("min_rating", "").strip()

        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(specialization__icontains=q) |
                Q(qualification__icontains=q) |
                Q(bio__icontains=q)
            )

        if specialization:
            qs = qs.filter(specialization__icontains=specialization)

        if min_exp.isdigit():
            qs = qs.filter(experience_years__gte=int(min_exp))

        try:
            if min_rating:
                qs = qs.filter(rating__gte=float(min_rating))
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
        # If your components need dropdown data (e.g., specializations list), we’ll wire them after seeing components/DoctorFilter.html
        return ctx




User = get_user_model()

class DoctorDetailView(View):
    def get(self, request, id):
        doctor = get_object_or_404(User, id=id)
        profile = getattr(doctor, "doctors_doctor_profile", None)

        # Fetch available slots for next 7 days
        today = datetime.now()
        next_week = today + timedelta(days=7)
        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__range=(today, next_week),
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).values_list("scheduled_time", flat=True)

        # Generate hourly slots (e.g., 9am to 5pm)
        slots = []
        for day in range(7):
            date = today + timedelta(days=day)
            for hour in range(9, 17):  # 9am to 5pm
                slot_time = datetime(date.year, date.month, date.day, hour)
                if slot_time not in booked_slots:
                    slots.append(slot_time)

        context = {
            "doctor": doctor,
            "profile": profile,
            "available_slots": slots,
        }
        return render(request, "doctors/doctor_detail.html", context)
