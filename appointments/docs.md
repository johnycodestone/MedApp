# Appointments App — Developer Reference

## Purpose
Handles booking, rescheduling, cancelling, and tracking appointments between patients and doctors.

## Models
- `Appointment`: Core model linking patient, doctor, time, and status.
- `AppointmentStatus`: Enum for status values.

## Key Files
- `services.py`: Business logic for appointment operations.
- `repositories.py`: Centralized DB access.
- `serializers.py`: DRF validation and shaping.
- `views.py`: API endpoints via ViewSet.
- `tasks.py`: Background reminders via Celery.
- `signals.py`: Triggers reminders on creation.

## API Endpoints
- `GET /appointments/`: List upcoming appointments.
- `POST /appointments/`: Book a new appointment.
- `PUT /appointments/<id>/`: Reschedule.
- `DELETE /appointments/<id>/`: Cancel.

## Notes
- Unique constraint on doctor + scheduled_time.
- Reminder emails sent asynchronously.
