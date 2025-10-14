from django.shortcuts import render

# Create your views here.

# patients/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import PatientProfileSerializer, SaveDoctorSerializer, MedicalRecordUploadSerializer
from .services import ensure_profile_for_user, add_favorite_doctor, delete_favorite_doctor, upload_medical_record, get_records

class PatientProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = ensure_profile_for_user(request.user)
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data)

class SaveDoctorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SaveDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor_id = serializer.validated_data['doctor_id']
        obj, created = add_favorite_doctor(request.user, doctor_id)
        return Response({'saved': created}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        serializer = SaveDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delete_favorite_doctor(request.user, serializer.validated_data['doctor_id'])
        return Response(status=status.HTTP_204_NO_CONTENT)

class MedicalRecordUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MedicalRecordUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = upload_medical_record(request.user, serializer.validated_data['title'], request.FILES['file'], serializer.validated_data.get('notes', ''))
        return Response(MedicalRecordUploadSerializer(record).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        records = get_records(request.user)
        serializer = MedicalRecordUploadSerializer(records, many=True)
        return Response(serializer.data)

# Simple view to render the staging.html template added by Waqar
def staging_view(request):
    return render(request, 'pages/staging.html')