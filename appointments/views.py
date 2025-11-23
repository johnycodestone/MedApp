from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from .services import AppointmentService
from .permissions import IsOwnerOrDoctor



class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """List upcoming appointments for the authenticated user."""
        appointments = AppointmentService.get_upcoming_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new appointment."""
        data = request.data
        from django.contrib.auth import get_user_model
        User = get_user_model()

        doctor_id = data.get('doctor')
        try:
            doctor = User.objects.get(id=doctor_id)  # ✅ Convert ID to User instance
        except User.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_400_BAD_REQUEST)

        appointment = AppointmentService.create_appointment(
            patient=request.user,
            doctor=doctor,  # ✅ Pass actual User instance
            scheduled_time=data.get('scheduled_time'),
            reason=data.get('reason')
        )
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



    def update(self, request, *args, **kwargs):
        """Reschedule an appointment."""
        pk = kwargs.get('pk')
        new_time = request.data.get('scheduled_time')
        appointment = AppointmentService.reschedule_appointment(pk, new_time)
        if appointment:
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)
        return Response({'error': 'Unable to reschedule'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Cancel an appointment."""
        pk = kwargs.get('pk')
        appointment = AppointmentService.cancel_appointment(pk, request.user)
        if appointment:
            return Response({'status': 'cancelled'})
        return Response({'error': 'Unauthorized or not found'}, status=status.HTTP_403_FORBIDDEN)

from django.views.generic import CreateView
from .models import Appointment
from .forms import AppointmentForm  # use your custom form

class AppointmentCreateView(CreateView):
    """
    Frontend view for booking a new appointment.
    - Uses AppointmentForm for clean field rendering and validation.
    - Renders appointments/create.html template.
    - Redirects to /appointments/ after successful booking.
    - Adds breadcrumbs context for navigation consistency.
    """
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create.html'
    success_url = '/appointments/'

    def get_context_data(self, **kwargs):
        """
        Extend context with breadcrumbs for includes/breadcrumbs.html.
        Ensures navigation trail appears correctly in the template.
        """
        context = super().get_context_data(**kwargs)
        context["crumbs"] = [
            {"label": "Home", "url": "/"},
            {"label": "Appointments", "url": "/appointments/"},
            {"label": "Book", "url": None},
        ]
        return context


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Appointment

@login_required
def appointment_list_view(request):
    """
    Appointment list view (template-based).
    - Requires authentication (@login_required).
    - Flexible: filters appointments based on the role of the logged-in user.
      * Patients → appointments where they are the patient.
      * Doctors → appointments where they are the doctor.
      * Admins → all appointments (future extension).
    - Orders appointments by scheduled_time (latest first).
    - Passes breadcrumb trail for navigation context.
    - Renders appointments/appointment_list.html with appointments + crumbs.
    """

    user = request.user

    # Default: patient view
    appointments = Appointment.objects.filter(patient=user)

    # Future-proof role handling
    if hasattr(user, "is_doctor") and user.is_doctor:
        # Doctor role → show appointments where they are the doctor
        appointments = Appointment.objects.filter(doctor=user)

    elif hasattr(user, "is_staff") and user.is_staff:
        # Admin role → show all appointments
        appointments = Appointment.objects.all()

    # Optimize queries (doctor/patient info preloaded)
    appointments = appointments.select_related("doctor", "patient").order_by("-scheduled_time")

    # Breadcrumbs for navigation
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
        }
    )
