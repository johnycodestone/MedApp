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
