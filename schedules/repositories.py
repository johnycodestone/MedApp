"""
schedules/repositories.py

Data access layer for schedule management.
Encapsulates all database queries for schedules.
"""

from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import datetime, timedelta, time
from typing import Optional, List
from .models import Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride


class DutyRepository:
    """Repository for Duty model operations"""
    
    @staticmethod
    def create_duty(doctor, hospital, duty_type, start_date, **kwargs) -> Duty:
        """Create a new duty"""
        return Duty.objects.create(
            doctor=doctor,
            hospital=hospital,
            duty_type=duty_type,
            start_date=start_date,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(duty_id: int) -> Optional[Duty]:
        """Get duty by ID"""
        try:
            return Duty.objects.select_related(
                'doctor__user', 'hospital__user', 'department'
            ).get(id=duty_id)
        except Duty.DoesNotExist:
            return None
    
    @staticmethod
    def get_doctor_duties(doctor, is_active: bool = True) -> List[Duty]:
        """Get all duties for a doctor"""
        queryset = Duty.objects.filter(doctor=doctor)
        if is_active:
            queryset = queryset.filter(is_active=True)
        return queryset.select_related('hospital__user', 'department')
    
    @staticmethod
    def get_hospital_duties(hospital, is_active: bool = True) -> List[Duty]:
        """Get all duties at a hospital"""
        queryset = Duty.objects.filter(hospital=hospital)
        if is_active:
            queryset = queryset.filter(is_active=True)
        return queryset.select_related('doctor__user', 'department')
    
    @staticmethod
    def get_current_duties(doctor) -> List[Duty]:
        """Get currently active duties for a doctor"""
        today = timezone.now().date()
        return Duty.objects.filter(
            doctor=doctor,
            is_active=True,
            start_date__lte=today
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        ).select_related('hospital__user', 'department')
    
    @staticmethod
    def update_duty(duty: Duty, **fields) -> Duty:
        """Update duty fields"""
        for field, value in fields.items():
            setattr(duty, field, value)
        duty.save()
        return duty
    
    @staticmethod
    def deactivate_duty(duty: Duty) -> Duty:
        """Deactivate a duty"""
        duty.is_active = False
        duty.save()
        return duty


class ShiftRepository:
    """Repository for Shift model operations"""
    
    @staticmethod
    def create_shift(duty, day_of_week, start_time, end_time, **kwargs) -> Shift:
        """Create a new shift"""
        return Shift.objects.create(
            duty=duty,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(shift_id: int) -> Optional[Shift]:
        """Get shift by ID"""
        try:
            return Shift.objects.select_related(
                'duty__doctor__user', 'duty__hospital__user'
            ).get(id=shift_id)
        except Shift.DoesNotExist:
            return None
    
    @staticmethod
    def get_duty_shifts(duty, is_active: bool = True) -> List[Shift]:
        """Get all shifts for a duty"""
        queryset = Shift.objects.filter(duty=duty)
        if is_active:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('day_of_week', 'start_time')
    
    @staticmethod
    def get_doctor_shifts(doctor, day_of_week: int = None) -> List[Shift]:
        """Get all shifts for a doctor"""
        queryset = Shift.objects.filter(
            duty__doctor=doctor,
            duty__is_active=True,
            is_active=True
        )
        if day_of_week is not None:
            queryset = queryset.filter(day_of_week=day_of_week)
        return queryset.select_related('duty__hospital__user')
    
    @staticmethod
    def get_shifts_for_date(doctor, date) -> List[Shift]:
        """Get shifts for a specific date"""
        day_of_week = date.weekday()
        today = timezone.now().date()
        
        return Shift.objects.filter(
            duty__doctor=doctor,
            duty__is_active=True,
            duty__start_date__lte=date,
            is_active=True,
            day_of_week=day_of_week
        ).filter(
            Q(duty__end_date__isnull=True) | Q(duty__end_date__gte=date)
        ).select_related('duty__hospital__user')
    
    @staticmethod
    def update_shift(shift: Shift, **fields) -> Shift:
        """Update shift fields"""
        for field, value in fields.items():
            setattr(shift, field, value)
        shift.save()
        return shift
    
    @staticmethod
    def delete_shift(shift: Shift):
        """Delete a shift"""
        shift.delete()
    
    @staticmethod
    def bulk_create_shifts(shifts_data: List[dict]) -> List[Shift]:
        """Bulk create shifts"""
        shifts = [Shift(**data) for data in shifts_data]
        return Shift.objects.bulk_create(shifts)


class AvailabilitySlotRepository:
    """Repository for AvailabilitySlot model operations"""
    
    @staticmethod
    def create_slot(shift, date, start_time, end_time, **kwargs) -> AvailabilitySlot:
        """Create a new availability slot"""
        return AvailabilitySlot.objects.create(
            shift=shift,
            date=date,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(slot_id: int) -> Optional[AvailabilitySlot]:
        """Get slot by ID"""
        try:
            return AvailabilitySlot.objects.select_related(
                'shift__duty__doctor__user', 'shift__duty__hospital__user'
            ).get(id=slot_id)
        except AvailabilitySlot.DoesNotExist:
            return None
    
    @staticmethod
    def get_available_slots(doctor, date, is_booked: bool = False) -> List[AvailabilitySlot]:
        """Get available slots for a doctor on a date"""
        return AvailabilitySlot.objects.filter(
            shift__duty__doctor=doctor,
            date=date,
            is_available=True,
            is_booked=is_booked
        ).select_related('shift__duty__hospital__user').order_by('start_time')
    
    @staticmethod
    def get_slots_by_date_range(doctor, start_date, end_date) -> List[AvailabilitySlot]:
        """Get slots for a doctor in date range"""
        return AvailabilitySlot.objects.filter(
            shift__duty__doctor=doctor,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('shift__duty__hospital__user').order_by('date', 'start_time')
    
    @staticmethod
    def get_booked_slots(patient) -> List[AvailabilitySlot]:
        """Get slots booked by a patient"""
        return AvailabilitySlot.objects.filter(
            booked_by=patient,
            is_booked=True
        ).select_related(
            'shift__duty__doctor__user', 'shift__duty__hospital__user'
        ).order_by('date', 'start_time')
    
    @staticmethod
    def mark_slot_as_booked(slot: AvailabilitySlot, patient, appointment=None) -> AvailabilitySlot:
        """Mark slot as booked"""
        slot.mark_as_booked(patient, appointment)
        return slot
    
    @staticmethod
    def mark_slot_as_available(slot: AvailabilitySlot) -> AvailabilitySlot:
        """Mark slot as available"""
        slot.mark_as_available()
        return slot
    
    @staticmethod
    def bulk_create_slots(slots_data: List[dict]) -> List[AvailabilitySlot]:
        """Bulk create availability slots"""
        slots = [AvailabilitySlot(**data) for data in slots_data]
        return AvailabilitySlot.objects.bulk_create(slots, ignore_conflicts=True)
    
    @staticmethod
    def delete_future_slots(shift, from_date) -> int:
        """Delete future slots for a shift"""
        return AvailabilitySlot.objects.filter(
            shift=shift,
            date__gte=from_date,
            is_booked=False
        ).delete()[0]


class DoctorLeaveRepository:
    """Repository for DoctorLeave model operations"""
    
    @staticmethod
    def create_leave(doctor, leave_type, start_date, end_date, reason, **kwargs) -> DoctorLeave:
        """Create a new leave request"""
        return DoctorLeave.objects.create(
            doctor=doctor,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(leave_id: int) -> Optional[DoctorLeave]:
        """Get leave by ID"""
        try:
            return DoctorLeave.objects.select_related(
                'doctor__user', 'approved_by'
            ).get(id=leave_id)
        except DoctorLeave.DoesNotExist:
            return None
    
    @staticmethod
    def get_doctor_leaves(doctor, status: str = None) -> List[DoctorLeave]:
        """Get leaves for a doctor"""
        queryset = DoctorLeave.objects.filter(doctor=doctor)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-start_date')
    
    @staticmethod
    def get_active_leaves(doctor) -> List[DoctorLeave]:
        """Get currently active leaves for a doctor"""
        today = timezone.now().date()
        return DoctorLeave.objects.filter(
            doctor=doctor,
            status='APPROVED',
            start_date__lte=today,
            end_date__gte=today
        )
    
    @staticmethod
    def get_pending_leaves(hospital=None) -> List[DoctorLeave]:
        """Get pending leave requests"""
        queryset = DoctorLeave.objects.filter(status='PENDING')
        if hospital:
            queryset = queryset.filter(
                doctor__duties__hospital=hospital,
                doctor__duties__is_active=True
            ).distinct()
        return queryset.select_related('doctor__user').order_by('start_date')
    
    @staticmethod
    def check_leave_overlap(doctor, start_date, end_date, exclude_id=None) -> bool:
        """Check if leave overlaps with existing leaves"""
        queryset = DoctorLeave.objects.filter(
            doctor=doctor,
            status__in=['PENDING', 'APPROVED']
        ).filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        )
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        return queryset.exists()
    
    @staticmethod
    def approve_leave(leave: DoctorLeave, approved_by, notes: str = '') -> DoctorLeave:
        """Approve leave request"""
        leave.status = 'APPROVED'
        leave.approved_by = approved_by
        leave.approval_notes = notes
        leave.save()
        return leave
    
    @staticmethod
    def reject_leave(leave: DoctorLeave, rejected_by, notes: str = '') -> DoctorLeave:
        """Reject leave request"""
        leave.status = 'REJECTED'
        leave.approved_by = rejected_by
        leave.approval_notes = notes
        leave.save()
        return leave
    
    @staticmethod
    def cancel_leave(leave: DoctorLeave) -> DoctorLeave:
        """Cancel leave request"""
        leave.status = 'CANCELLED'
        leave.save()
        return leave


class ScheduleOverrideRepository:
    """Repository for ScheduleOverride model operations"""
    
    @staticmethod
    def create_override(doctor, date, is_available, reason, created_by, **kwargs) -> ScheduleOverride:
        """Create a schedule override"""
        return ScheduleOverride.objects.create(
            doctor=doctor,
            date=date,
            is_available=is_available,
            reason=reason,
            created_by=created_by,
            **kwargs
        )
    
    @staticmethod
    def get_by_id(override_id: int) -> Optional[ScheduleOverride]:
        """Get override by ID"""
        try:
            return ScheduleOverride.objects.select_related(
                'doctor__user', 'created_by'
            ).get(id=override_id)
        except ScheduleOverride.DoesNotExist:
            return None
    
    @staticmethod
    def get_override_for_date(doctor, date) -> Optional[ScheduleOverride]:
        """Get override for specific date"""
        try:
            return ScheduleOverride.objects.get(doctor=doctor, date=date)
        except ScheduleOverride.DoesNotExist:
            return None
    
    @staticmethod
    def get_doctor_overrides(doctor, from_date=None) -> List[ScheduleOverride]:
        """Get overrides for a doctor"""
        queryset = ScheduleOverride.objects.filter(doctor=doctor)
        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        return queryset.order_by('date')
    
    @staticmethod
    def update_override(override: ScheduleOverride, **fields) -> ScheduleOverride:
        """Update override"""
        for field, value in fields.items():
            setattr(override, field, value)
        override.save()
        return override
    
    @staticmethod
    def delete_override(override: ScheduleOverride):
        """Delete override"""
        override.delete()