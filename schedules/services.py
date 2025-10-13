"""
schedules/services.py

Business logic layer for schedule management.
Handles duty assignments, shift creation, slot generation, and leave management.
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, time
from typing import List, Tuple, Optional, Dict
from .models import Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride
from .repositories import (
    DutyRepository, ShiftRepository, AvailabilitySlotRepository,
    DoctorLeaveRepository, ScheduleOverrideRepository
)


class DutyService:
    """Service for managing doctor duties"""
    
    @staticmethod
    @transaction.atomic
    def create_duty(doctor, hospital, duty_type, start_date, **kwargs) -> Duty:
        """
        Create a new duty for a doctor at a hospital.
        
        Args:
            doctor: DoctorProfile instance
            hospital: HospitalProfile instance
            duty_type: Type of duty
            start_date: Start date
            **kwargs: Additional fields
        
        Returns:
            Created Duty instance
        """
        duty = DutyRepository.create_duty(
            doctor=doctor,
            hospital=hospital,
            duty_type=duty_type,
            start_date=start_date,
            **kwargs
        )
        
        return duty
    
    @staticmethod
    def get_doctor_duties(doctor, is_active: bool = True) -> List[Duty]:
        """Get all duties for a doctor"""
        return DutyRepository.get_doctor_duties(doctor, is_active)
    
    @staticmethod
    def get_current_duties(doctor) -> List[Duty]:
        """Get currently active duties"""
        return DutyRepository.get_current_duties(doctor)
    
    @staticmethod
    @transaction.atomic
    def update_duty(duty_id: int, **fields) -> Tuple[bool, str, Optional[Duty]]:
        """Update duty"""
        duty = DutyRepository.get_by_id(duty_id)
        if not duty:
            return False, "Duty not found", None
        
        updated_duty = DutyRepository.update_duty(duty, **fields)
        return True, "Duty updated successfully", updated_duty
    
    @staticmethod
    @transaction.atomic
    def end_duty(duty_id: int, end_date) -> Tuple[bool, str]:
        """End a duty"""
        duty = DutyRepository.get_by_id(duty_id)
        if not duty:
            return False, "Duty not found"
        
        duty.end_date = end_date
        duty.is_active = False
        duty.save()
        
        return True, "Duty ended successfully"


class ShiftService:
    """Service for managing work shifts"""
    
    @staticmethod
    @transaction.atomic
    def create_shift(duty_id: int, day_of_week: int, start_time, end_time, **kwargs) -> Tuple[bool, str, Optional[Shift]]:
        """Create a new shift"""
        duty = DutyRepository.get_by_id(duty_id)
        if not duty:
            return False, "Duty not found", None
        
        shift = ShiftRepository.create_shift(
            duty=duty,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )
        
        return True, "Shift created successfully", shift
    
    @staticmethod
    @transaction.atomic
    def create_multiple_shifts(duty_id: int, days_of_week: List[int], 
                               start_time, end_time, **kwargs) -> Tuple[bool, str, List[Shift]]:
        """
        Create shifts for multiple days of the week.
        
        Args:
            duty_id: Duty ID
            days_of_week: List of day numbers (0-6)
            start_time: Shift start time
            end_time: Shift end time
            **kwargs: Additional shift fields
        
        Returns:
            Tuple of (success, message, created_shifts)
        """
        duty = DutyRepository.get_by_id(duty_id)
        if not duty:
            return False, "Duty not found", []
        
        shifts_data = []
        for day in days_of_week:
            shifts_data.append({
                'duty': duty,
                'day_of_week': day,
                'start_time': start_time,
                'end_time': end_time,
                **kwargs
            })
        
        shifts = ShiftRepository.bulk_create_shifts(shifts_data)
        return True, f"{len(shifts)} shifts created successfully", shifts
    
    @staticmethod
    def get_doctor_shifts(doctor, day_of_week: int = None) -> List[Shift]:
        """Get shifts for a doctor"""
        return ShiftRepository.get_doctor_shifts(doctor, day_of_week)
    
    @staticmethod
    def get_shifts_for_date(doctor, date) -> List[Shift]:
        """Get shifts for a specific date"""
        return ShiftRepository.get_shifts_for_date(doctor, date)
    
    @staticmethod
    @transaction.atomic
    def update_shift(shift_id: int, **fields) -> Tuple[bool, str, Optional[Shift]]:
        """Update a shift"""
        shift = ShiftRepository.get_by_id(shift_id)
        if not shift:
            return False, "Shift not found", None
        
        updated_shift = ShiftRepository.update_shift(shift, **fields)
        return True, "Shift updated successfully", updated_shift
    
    @staticmethod
    @transaction.atomic
    def delete_shift(shift_id: int) -> Tuple[bool, str]:
        """Delete a shift"""
        shift = ShiftRepository.get_by_id(shift_id)
        if not shift:
            return False, "Shift not found"
        
        # Delete future unbooked slots
        today = timezone.now().date()
        AvailabilitySlotRepository.delete_future_slots(shift, today)
        
        ShiftRepository.delete_shift(shift)
        return True, "Shift deleted successfully"


class AvailabilitySlotService:
    """Service for managing availability slots"""
    
    @staticmethod
    @transaction.atomic
    def generate_slots_for_shift(shift_id: int, start_date, end_date, 
                                 slot_duration_minutes: int = 30) -> Tuple[bool, str, int]:
        """
        Generate availability slots for a shift.
        
        Args:
            shift_id: Shift ID
            start_date: Start date for slot generation
            end_date: End date for slot generation
            slot_duration_minutes: Duration of each slot in minutes
        
        Returns:
            Tuple of (success, message, slots_created_count)
        """
        shift = ShiftRepository.get_by_id(shift_id)
        if not shift:
            return False, "Shift not found", 0
        
        # Generate slots for each occurrence of the shift day
        slots_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Check if this date matches the shift's day of week
            if current_date.weekday() == shift.day_of_week:
                # Check for overrides
                override = ScheduleOverrideRepository.get_override_for_date(
                    shift.duty.doctor, current_date
                )
                
                if override and not override.is_available:
                    # Skip this date
                    current_date += timedelta(days=1)
                    continue
                
                # Check for leaves
                leaves = DoctorLeaveRepository.get_active_leaves(shift.duty.doctor)
                is_on_leave = any(
                    leave.start_date <= current_date <= leave.end_date
                    for leave in leaves
                )
                
                if is_on_leave:
                    current_date += timedelta(days=1)
                    continue
                
                # Generate time slots
                current_time = shift.start_time
                end_time = shift.end_time
                
                while True:
                    # Calculate slot end time
                    slot_end = (
                        datetime.combine(current_date, current_time) + 
                        timedelta(minutes=slot_duration_minutes)
                    ).time()
                    
                    # Check if slot end exceeds shift end
                    if slot_end > end_time:
                        break
                    
                    # Skip break time
                    if shift.break_start and shift.break_end:
                        if not (slot_end <= shift.break_start or current_time >= shift.break_end):
                            current_time = (
                                datetime.combine(current_date, current_time) + 
                                timedelta(minutes=slot_duration_minutes)
                            ).time()
                            continue
                    
                    slots_data.append({
                        'shift': shift,
                        'date': current_date,
                        'start_time': current_time,
                        'end_time': slot_end,
                        'is_available': True,
                        'is_booked': False
                    })
                    
                    # Move to next slot
                    current_time = slot_end
            
            current_date += timedelta(days=1)
        
        # Bulk create slots
        created_slots = AvailabilitySlotRepository.bulk_create_slots(slots_data)
        
        return True, f"{len(created_slots)} slots generated successfully", len(created_slots)
    
    @staticmethod
    def get_available_slots(doctor, date) -> List[AvailabilitySlot]:
        """Get available slots for a doctor on a specific date"""
        return AvailabilitySlotRepository.get_available_slots(doctor, date, is_booked=False)
    
    @staticmethod
    def get_doctor_availability(doctor, start_date, end_date) -> Dict:
        """
        Get doctor availability for a date range.
        
        Returns:
            Dictionary with dates as keys and slot counts as values
        """
        slots = AvailabilitySlotRepository.get_slots_by_date_range(
            doctor, start_date, end_date
        )
        
        availability = {}
        for slot in slots:
            date_str = slot.date.isoformat()
            if date_str not in availability:
                availability[date_str] = {
                    'total_slots': 0,
                    'available_slots': 0,
                    'booked_slots': 0
                }
            
            availability[date_str]['total_slots'] += 1
            if slot.is_available and not slot.is_booked:
                availability[date_str]['available_slots'] += 1
            if slot.is_booked:
                availability[date_str]['booked_slots'] += 1
        
        return availability
    
    @staticmethod
    @transaction.atomic
    def book_slot(slot_id: int, patient, appointment=None) -> Tuple[bool, str]:
        """Book an availability slot"""
        slot = AvailabilitySlotRepository.get_by_id(slot_id)
        if not slot:
            return False, "Slot not found"
        
        if not slot.is_available or slot.is_booked:
            return False, "Slot is not available for booking"
        
        AvailabilitySlotRepository.mark_slot_as_booked(slot, patient, appointment)
        return True, "Slot booked successfully"
    
    @staticmethod
    @transaction.atomic
    def cancel_slot_booking(slot_id: int) -> Tuple[bool, str]:
        """Cancel a slot booking"""
        slot = AvailabilitySlotRepository.get_by_id(slot_id)
        if not slot:
            return False, "Slot not found"
        
        if not slot.is_booked:
            return False, "Slot is not booked"
        
        AvailabilitySlotRepository.mark_slot_as_available(slot)
        return True, "Booking cancelled successfully"


class DoctorLeaveService:
    """Service for managing doctor leaves"""
    
    @staticmethod
    @transaction.atomic
    def request_leave(doctor, leave_type, start_date, end_date, reason) -> Tuple[bool, str, Optional[DoctorLeave]]:
        """
        Request leave for a doctor.
        
        Args:
            doctor: DoctorProfile instance
            leave_type: Type of leave
            start_date: Leave start date
            end_date: Leave end date
            reason: Leave reason
        
        Returns:
            Tuple of (success, message, leave)
        """
        # Check for overlapping leaves
        if DoctorLeaveRepository.check_leave_overlap(doctor, start_date, end_date):
            return False, "Leave request overlaps with existing leave", None
        
        leave = DoctorLeaveRepository.create_leave(
            doctor=doctor,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        return True, "Leave request submitted successfully", leave
    
    @staticmethod
    @transaction.atomic
    def approve_leave(leave_id: int, approved_by, notes: str = '') -> Tuple[bool, str]:
        """Approve a leave request"""
        leave = DoctorLeaveRepository.get_by_id(leave_id)
        if not leave:
            return False, "Leave request not found"
        
        if leave.status != 'PENDING':
            return False, "Only pending leave requests can be approved"
        
        DoctorLeaveRepository.approve_leave(leave, approved_by, notes)
        
        # Mark slots as unavailable for leave period
        AvailabilitySlotService._handle_leave_slots(leave)
        
        return True, "Leave request approved"
    
    @staticmethod
    @transaction.atomic
    def reject_leave(leave_id: int, rejected_by, notes: str = '') -> Tuple[bool, str]:
        """Reject a leave request"""
        leave = DoctorLeaveRepository.get_by_id(leave_id)
        if not leave:
            return False, "Leave request not found"
        
        if leave.status != 'PENDING':
            return False, "Only pending leave requests can be rejected"
        
        DoctorLeaveRepository.reject_leave(leave, rejected_by, notes)
        return True, "Leave request rejected"
    
    @staticmethod
    def get_doctor_leaves(doctor, status: str = None) -> List[DoctorLeave]:
        """Get leaves for a doctor"""
        return DoctorLeaveRepository.get_doctor_leaves(doctor, status)
    
    @staticmethod
    def get_pending_leaves(hospital=None) -> List[DoctorLeave]:
        """Get pending leave requests"""
        return DoctorLeaveRepository.get_pending_leaves(hospital)
    
    @staticmethod
    def _handle_leave_slots(leave: DoctorLeave):
        """Mark slots as unavailable during leave period"""
        slots = AvailabilitySlotRepository.get_slots_by_date_range(
            leave.doctor, leave.start_date, leave.end_date
        )
        
        for slot in slots:
            if not slot.is_booked:
                slot.is_available = False
                slot.save()


class ScheduleOverrideService:
    """Service for managing schedule overrides"""
    
    @staticmethod
    @transaction.atomic
    def create_override(doctor, date, is_available, reason, created_by, **kwargs) -> Tuple[bool, str, Optional[ScheduleOverride]]:
        """
        Create a schedule override.
        
        Args:
            doctor: DoctorProfile instance
            date: Override date
            is_available: Whether doctor is available
            reason: Override reason
            created_by: User creating override
            **kwargs: Additional fields
        
        Returns:
            Tuple of (success, message, override)
        """
        # Check if override already exists
        existing = ScheduleOverrideRepository.get_override_for_date(doctor, date)
        if existing:
            return False, "Override already exists for this date", None
        
        override = ScheduleOverrideRepository.create_override(
            doctor=doctor,
            date=date,
            is_available=is_available,
            reason=reason,
            created_by=created_by,
            **kwargs
        )
        
        # Update existing slots for this date
        if not is_available:
            slots = AvailabilitySlotRepository.get_available_slots(doctor, date)
            for slot in slots:
                if not slot.is_booked:
                    slot.is_available = False
                    slot.save()
        
        return True, "Schedule override created successfully", override
    
    @staticmethod
    @transaction.atomic
    def update_override(override_id: int, **fields) -> Tuple[bool, str, Optional[ScheduleOverride]]:
        """Update a schedule override"""
        override = ScheduleOverrideRepository.get_by_id(override_id)
        if not override:
            return False, "Override not found", None
        
        updated_override = ScheduleOverrideRepository.update_override(override, **fields)
        return True, "Override updated successfully", updated_override
    
    @staticmethod
    @transaction.atomic
    def delete_override(override_id: int) -> Tuple[bool, str]:
        """Delete a schedule override"""
        override = ScheduleOverrideRepository.get_by_id(override_id)
        if not override:
            return False, "Override not found"
        
        ScheduleOverrideRepository.delete_override(override)
        return True, "Override deleted successfully"
    
    @staticmethod
    def get_doctor_overrides(doctor, from_date=None) -> List[ScheduleOverride]:
        """Get overrides for a doctor"""
        return ScheduleOverrideRepository.get_doctor_overrides(doctor, from_date)


class ScheduleAnalyticsService:
    """Service for schedule analytics and reporting"""
    
    @staticmethod
    def get_doctor_schedule_summary(doctor, start_date, end_date) -> Dict:
        """
        Get comprehensive schedule summary for a doctor.
        
        Returns:
            Dictionary with schedule statistics
        """
        # Get shifts
        shifts = ShiftRepository.get_doctor_shifts(doctor)
        
        # Get slots
        slots = AvailabilitySlotRepository.get_slots_by_date_range(
            doctor, start_date, end_date
        )
        
        # Get leaves
        leaves = DoctorLeaveRepository.get_doctor_leaves(doctor, status='APPROVED')
        active_leaves = [l for l in leaves if l.is_active()]
        
        # Calculate statistics
        total_slots = len(slots)
        available_slots = sum(1 for s in slots if s.is_available and not s.is_booked)
        booked_slots = sum(1 for s in slots if s.is_booked)
        
        # Group by date
        dates_with_slots = set(slot.date for slot in slots)
        working_days = len(dates_with_slots)
        
        return {
            'total_shifts': len(shifts),
            'total_slots': total_slots,
            'available_slots': available_slots,
            'booked_slots': booked_slots,
            'booking_rate': (booked_slots / total_slots * 100) if total_slots > 0 else 0,
            'working_days': working_days,
            'active_leaves': len(active_leaves),
            'shifts_by_day': {
                shift.get_day_of_week_display(): {
                    'start_time': shift.start_time.strftime('%H:%M'),
                    'end_time': shift.end_time.strftime('%H:%M'),
                    'duration_minutes': shift.duration_minutes()
                }
                for shift in shifts
            }
        }
    
    @staticmethod
    def get_weekly_schedule(doctor, week_start) -> Dict:
        """
        Get weekly schedule for a doctor.
        
        Args:
            doctor: DoctorProfile instance
            week_start: Monday of the week
        
        Returns:
            Dictionary with daily schedules
        """
        week_end = week_start + timedelta(days=6)
        
        weekly_schedule = {}
        current_date = week_start
        
        while current_date <= week_end:
            day_name = current_date.strftime('%A')
            
            # Get shifts for this day
            shifts = ShiftRepository.get_shifts_for_date(doctor, current_date)
            
            # Get slots for this day
            slots = AvailabilitySlotRepository.get_available_slots(doctor, current_date)
            
            # Check for override
            override = ScheduleOverrideRepository.get_override_for_date(doctor, current_date)
            
            # Check for leave
            leaves = DoctorLeaveRepository.get_active_leaves(doctor)
            is_on_leave = any(
                leave.start_date <= current_date <= leave.end_date
                for leave in leaves
            )
            
            weekly_schedule[day_name] = {
                'date': current_date.isoformat(),
                'shifts': [
                    {
                        'start_time': shift.start_time.strftime('%H:%M'),
                        'end_time': shift.end_time.strftime('%H:%M'),
                        'hospital': shift.duty.hospital.hospital_name
                    }
                    for shift in shifts
                ],
                'total_slots': len(slots),
                'available_slots': sum(1 for s in slots if s.is_available and not s.is_booked),
                'booked_slots': sum(1 for s in slots if s.is_booked),
                'is_on_leave': is_on_leave,
                'has_override': override is not None,
                'override_available': override.is_available if override else None
            }
            
            current_date += timedelta(days=1)
        
        return weekly_schedule
    
    @staticmethod
    def get_hospital_doctor_schedules(hospital, date) -> List[Dict]:
        """
        Get all doctor schedules at a hospital for a date.
        
        Args:
            hospital: HospitalProfile instance
            date: Date to check
        
        Returns:
            List of doctor schedule summaries
        """
        duties = DutyRepository.get_hospital_duties(hospital, is_active=True)
        
        schedules = []
        for duty in duties:
            doctor = duty.doctor
            shifts = ShiftRepository.get_shifts_for_date(doctor, date)
            slots = AvailabilitySlotRepository.get_available_slots(doctor, date)
            
            if shifts:  # Only include doctors with shifts on this date
                schedules.append({
                    'doctor_id': doctor.id,
                    'doctor_name': doctor.user.get_full_name(),
                    'specialty': doctor.specialty,
                    'shifts': [
                        {
                            'start_time': shift.start_time.strftime('%H:%M'),
                            'end_time': shift.end_time.strftime('%H:%M')
                        }
                        for shift in shifts
                    ],
                    'total_slots': len(slots),
                    'available_slots': sum(1 for s in slots if s.is_available and not s.is_booked),
                    'booked_slots': sum(1 for s in slots if s.is_booked)
                })
        
        return schedules