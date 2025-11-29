from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_datetime
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponseForbidden

from .models import Appointment, AppointmentStatus
from .serializers import AppointmentSerializer
from .services import AppointmentService
from .permissions import IsOwnerOrDoctor
from .forms import AppointmentForm

from patients.models import PatientProfile
from doctors.models import DoctorProfile

# -------------------------------
# API ViewSet (DRF)
# -------------------------------
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        appointments = AppointmentService.get_upcoming_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        from django.contrib.auth import get_user_model
        User = get_user_model()

        doctor_id = data.get('doctor')
        try:
            doctor = User.objects.get(id=doctor_id)
        except User.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_400_BAD_REQUEST)

        scheduled_time = parse_datetime(data.get('scheduled_time'))
        if not scheduled_time:
            return Response({'error': 'Invalid scheduled_time format'}, status=status.HTTP_400_BAD_REQUEST)

        appointment = AppointmentService.create_appointment(
            patient=request.user,
            doctor=doctor,
            scheduled_time=scheduled_time,
            reason=data.get('reason')
        )
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        new_time = parse_datetime(request.data.get('scheduled_time'))
        if not new_time:
            return Response({'error': 'Invalid scheduled_time format'}, status=status.HTTP_400_BAD_REQUEST)

        appointment = AppointmentService.reschedule_appointment(pk, new_time)
        if appointment:
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)
        return Response({'error': 'Unable to reschedule'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        appointment = AppointmentService.cancel_appointment(pk, request.user)
        if appointment:
            return Response({'status': 'cancelled'})
        return Response({'error': 'Unauthorized or not found'}, status=status.HTTP_403_FORBIDDEN)


# -------------------------------
# Frontend CreateView
# -------------------------------
class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create.html'
    success_url = '/appointments/'

    def form_valid(self, form):
        appointment = form.save(commit=False)
        try:
            appointment.patient = self.request.user.patientprofile
        except PatientProfile.DoesNotExist:
            return redirect('patients:profile')
        appointment.status = AppointmentStatus.PENDING
        appointment.save()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["crumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": "Appointments", "url": "/appointments/"},
            {"label": "Book", "url": None},
        ]
        return context


# -------------------------------
# Appointment List View (Frontend)
# -------------------------------
@login_required
def appointment_list_view(request):
    user = request.user
    status_filter = request.GET.get("status")
    appointments = Appointment.objects.none()

    try:
        if hasattr(user, "patientprofile"):
            appointments = Appointment.objects.filter(patient=user.patientprofile)
        elif hasattr(user, "doctorprofile"):
            appointments = Appointment.objects.filter(doctor=user.doctorprofile)
        elif user.is_staff:
            appointments = Appointment.objects.all()
    except Exception:
        appointments = Appointment.objects.none()

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    appointments = appointments.select_related("doctor", "patient").order_by("-scheduled_time")

    crumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Appointments", "url": None},
    ]

    return render(
        request,
        "appointments/appointment_list.html",
        {
            "appointments": appointments,
            "crumbs": crumbs,
            "status_filter": status_filter,
        }
    )


# -------------------------------
# Appointment Cancel View
# -------------------------------
class AppointmentCancelView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        if request.user not in [appointment.patient.user, appointment.doctor.user]:
            return HttpResponseForbidden("You are not authorized to cancel this appointment.")
        appointment.status = AppointmentStatus.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])
        return redirect("appointments:appointment-list")


# -------------------------------
# Appointment Detail View (Frontend)
# -------------------------------
@login_required
def appointment_detail_view(request, pk):
    """
    Displays details for a single appointment.
    """
    appointment = get_object_or_404(Appointment.objects.select_related("doctor", "patient"), pk=pk)

    # Optional access control
    if request.user not in [appointment.patient.user, appointment.doctor.user] and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to view this appointment.")

    crumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Appointments", "url": "/appointments/"},
        {"label": "Details", "url": None},
    ]

    return render(request, "appointments/detail.html", {
        "appointment": appointment,
        "crumbs": crumbs,
    })
