"""
schedules/tasks.py

Celery background tasks for schedule management.
Handles automated slot generation, cleanup, and notifications.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .services import AvailabilitySlotService
from .repositories import ShiftRepository, AvailabilitySlotRepository
from doctors.models import DoctorProfile


@shared_task
def auto_generate_slots_for_all_doctors():
    """
    Automatically generate availability slots for all active doctors.
    Should be scheduled to run daily.
    """
    try:
        doctors = DoctorProfile.objects.filter(user__is_active=True)
        today = timezone.now().date()
        end_date = today + timedelta(days=30)  # Generate slots for next 30 days
        
        total_slots_created = 0
        
        for doctor in doctors:
            shifts = ShiftRepository.get_doctor_shifts(doctor)
            
            for shift in shifts:
                success, message, count = AvailabilitySlotService.generate_slots_for_shift(
                    shift_id=shift.id,
                    start_date=today,
                    end_date=end_date,
                    slot_duration_minutes=30
                )
                
                if success:
                    total_slots_created += count
        
        return f"Generated {total_slots_created} slots for {len(doctors)} doctors"
    
    except Exception as e:
        return f"Error generating slots: {str(e)}"


@shared_task
def generate_slots_for_doctor(doctor_id, days_ahead=30):
    """
    Generate availability slots for a specific doctor.
    
    Args:
        doctor_id: Doctor profile ID
        days_ahead: Number of days to generate slots for
    """
    try:
        from doctors.models import DoctorProfile
        
        doctor = DoctorProfile.objects.get(id=doctor_id)
        shifts = ShiftRepository.get_doctor_shifts(doctor)
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        total_slots = 0
        for shift in shifts:
            success, message, count = AvailabilitySlotService.generate_slots_for_shift(
                shift_id=shift.id,
                start_date=today,
                end_date=end_date,
                slot_duration_minutes=30
            )
            if success:
                total_slots += count
        
        return f"Generated {total_slots} slots for doctor {doctor.user.get_full_name()}"
    
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def cleanup_past_slots():
    """
    Clean up old unbooked availability slots.
    Should be scheduled to run daily.
    """
    try:
        cutoff_date = timezone.now().date() - timedelta(days=7)
        
        deleted_count = AvailabilitySlotRepository.get_slots_by_date_range(
            None, timezone.now().date() - timedelta(days=365), cutoff_date
        ).filter(is_booked=False).delete()[0]
        
        return f"Deleted {deleted_count} old unbooked slots"
    
    except Exception as e:
        return f"Error cleaning up slots: {str(e)}"


@shared_task
def send_appointment_reminders():
    """
    Send reminders for upcoming appointments.
    Should be scheduled to run hourly.
    """
    try:
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        slots = AvailabilitySlotRepository.get_slots_by_date_range(
            None, tomorrow, tomorrow
        ).filter(is_booked=True).select_related('booked_by', 'shift__duty__doctor__user')
        
        reminder_count = 0
        for slot in slots:
            # TODO: Send email/SMS reminder to patient
            # NotificationService.send_appointment_reminder(slot)
            reminder_count += 1
        
        return f"Sent {reminder_count} appointment reminders"
    
    except Exception as e:
        return f"Error sending reminders: {str(e)}"


@shared_task
def process_expired_leaves():
    """
    Process expired leaves and reactivate slots.
    Should be scheduled to run daily.
    """
    try:
        from .repositories import DoctorLeaveRepository
        
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Find leaves that ended yesterday
        from .models import DoctorLeave
        expired_leaves = DoctorLeave.objects.filter(
            status='APPROVED',
            end_date=yesterday
        )
        
        processed_count = 0
        for leave in expired_leaves:
            # Reactivate future slots for this doctor
            today = timezone.now().date()
            slots = AvailabilitySlotRepository.get_slots_by_date_range(
                leave.doctor, today, today + timedelta(days=30)
            ).filter(is_booked=False)
            
            for slot in slots:
                slot.is_available = True
                slot.save()
            
            processed_count += 1
        
        return f"Processed {processed_count} expired leaves"
    
    except Exception as e:
        return f"Error processing leaves: {str(e)}"


@shared_task
def notify_low_availability():
    """
    Notify doctors with low availability.
    Should be scheduled to run weekly.
    """
    try:
        from doctors.models import DoctorProfile
        
        doctors = DoctorProfile.objects.filter(user__is_active=True)
        today = timezone.now().date()
        week_ahead = today + timedelta(days=7)
        
        low_availability_doctors = []
        
        for doctor in doctors:
            slots = AvailabilitySlotRepository.get_slots_by_date_range(
                doctor, today, week_ahead
            )
            
            available_count = sum(1 for s in slots if s.is_available and not s.is_booked)
            
            # Alert if less than 20% availability
            if slots and (available_count / len(slots)) < 0.2:
                low_availability_doctors.append(doctor)
                # TODO: Send notification to doctor
        
        return f"Notified {len(low_availability_doctors)} doctors about low availability"
    
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def sync_shifts_with_duties():
    """
    Ensure all active duties have shifts configured.
    Should be scheduled to run weekly.
    """
    try:
        from .models import Duty
        
        duties_without_shifts = Duty.objects.filter(
            is_active=True,
            shifts__isnull=True
        ).distinct()
        
        # TODO: Notify hospital admins about duties without shifts
        
        return f"Found {len(duties_without_shifts)} duties without shifts"
    
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def generate_weekly_schedule_report():
    """
    Generate weekly schedule reports for hospitals.
    Should be scheduled to run weekly.
    """
    try:
        from hospitals.models import HospitalProfile
        from .services import ScheduleAnalyticsService
        
        hospitals = HospitalProfile.objects.filter(user__is_active=True)
        today = timezone.now().date()
        
        # Find Monday of current week
        week_start = today - timedelta(days=today.weekday())
        
        reports_generated = 0
        for hospital in hospitals:
            schedules = ScheduleAnalyticsService.get_hospital_doctor_schedules(
                hospital, today
            )
            
            # TODO: Send report to hospital admin
            reports_generated += 1
        
        return f"Generated {reports_generated} weekly schedule reports"
    
    except Exception as e:
        return f"Error: {str(e)}"