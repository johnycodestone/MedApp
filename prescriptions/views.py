# prescriptions/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, Http404
from django.db import models as dj_models
from .models import Prescription
from .serializers import PrescriptionSerializer
from .permissions import IsDoctorOrOwner
from .services import PrescriptionService

class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Prescription
    - GET /prescriptions/
    - POST /prescriptions/
    - GET/PUT/PATCH/DELETE /prescriptions/{id}/
    - GET /prescriptions/{id}/download_pdf/
    """
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrOwner]
    service = PrescriptionService()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Prescription.objects.all().prefetch_related("medications")
        return Prescription.objects.filter(dj_models.Q(patient=user) | dj_models.Q(doctor=user)).prefetch_related("medications")

    def perform_create(self, serializer):
        prescription = serializer.save()
        # Build & persist summary
        prescription.summary = self.service._build_summary(prescription)
        prescription.save(update_fields=["summary"])

    @action(detail=True, methods=["get"], url_path="download_pdf")
    def download_pdf(self, request, pk=None):
        prescription = self.get_object()
        pdf_bytes = self.service.generate_pdf(prescription)
        if not pdf_bytes:
            raise Http404("PDF not available")
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="prescription_{prescription.id}.pdf"'
        return response
