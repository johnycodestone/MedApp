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
