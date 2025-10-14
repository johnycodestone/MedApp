from django.shortcuts import render

# Create your views here.

# hospitals/views.py

from django.http import HttpResponse

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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import register_hospital, manage_department, manage_doctor, get_reports
from .serializers import HospitalSerializer, DepartmentSerializer, DoctorAssignmentSerializer, ReportSerializer

class HospitalProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        hospital = register_hospital(request.user, data.get("name"), address=data.get("address"), phone=data.get("phone"))
        return Response(HospitalSerializer(hospital).data, status=status.HTTP_201_CREATED)


class DepartmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        dept = manage_department(request.user.hospital_profile, "add", data["name"], data.get("description", ""))
        return Response(DepartmentSerializer(dept).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        data = request.data
        manage_department(request.user.hospital_profile, "remove", data["name"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DoctorDutyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        assign = manage_doctor(request.user.hospital_profile, data["doctor_id"], "assign", data.get("department"))
        return Response(DoctorAssignmentSerializer(assign).data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        data = request.data
        manage_doctor(request.user.hospital_profile, data["doctor_id"], "waive")
        return Response({"status": "Duty Waived"}, status=status.HTTP_200_OK)


class ReportListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reports = get_reports(request.user.hospital_profile)
        return Response(ReportSerializer(reports, many=True).data)
