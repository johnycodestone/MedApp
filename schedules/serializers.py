"""
schedules/serializers.py

DRF serializers for schedule management.
Handles validation and data transformation for schedule operations.
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride, ScheduleCategory, Schedule, ScheduleReminder


class DutySerializer(serializers.ModelSerializer):
    """
    Serializer for doctor duties.
    """
    
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.hospital_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    duty_type_display = serializers.CharField(source='get_duty_type_display', read_only=True)
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = Duty
        fields = [
            'id', 'doctor', 'doctor_name', 'hospital', 'hospital_name',
            'department', 'department_name', 'duty_type', 'duty_type_display',
            'start_date', 'end_date', 'is_active', 'is_current',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_current(self, obj):
        """Check if duty is currently active"""
        return obj.is_current()
    
    def validate(self, attrs):
        """Validate duty dates"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': "End date must be after start date"
            })
        
        return attrs


class ShiftSerializer(serializers.ModelSerializer):
    """
    Serializer for work shifts.
    """
    
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    duty_details = DutySerializer(source='duty', read_only=True)
    
    class Meta:
        model = Shift
        fields = [
            'id', 'duty', 'duty_details', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'max_appointments',
            'break_start', 'break_end', 'is_active',
            'duration_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_duration_minutes(self, obj):
        """Get shift duration in minutes"""
        return obj.duration_minutes()
    
    def validate(self, attrs):
        """Validate shift times"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        break_start = attrs.get('break_start')
        break_end = attrs.get('break_end')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': "End time must be after start time"
            })
        
        if break_start and break_end:
            if break_start >= break_end:
                raise serializers.ValidationError({
                    'break_end': "Break end time must be after break start time"
                })
            
            if start_time and end_time:
                if break_start < start_time or break_end > end_time:
                    raise serializers.ValidationError({
                        'break_start': "Break must be within shift hours"
                    })
        
        return attrs


class ShiftCreateSerializer(serializers.Serializer):
    """
    Serializer for creating multiple shifts at once.
    """
    
    duty = serializers.IntegerField(required=True)
    days_of_week = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=True
    )
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    max_appointments = serializers.IntegerField(default=10, min_value=1)
    break_start = serializers.TimeField(required=False, allow_null=True)
    break_end = serializers.TimeField(required=False, allow_null=True)
    
    def validate(self, attrs):
        """Validate shift creation data"""
        start_time = attrs['start_time']
        end_time = attrs['end_time']
        
        if start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': "End time must be after start time"
            })
        
        return attrs


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """
    Serializer for availability slots.
    """
    
    doctor_name = serializers.CharField(
        source='shift.duty.doctor.user.get_full_name',
        read_only=True
    )
    hospital_name = serializers.CharField(
        source='shift.duty.hospital.hospital_name',
        read_only=True
    )
    booked_by_name = serializers.CharField(
        source='booked_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'shift', 'doctor_name', 'hospital_name',
            'date', 'start_time', 'end_time',
            'is_available', 'is_booked', 'booked_by', 'booked_by_name',
            'appointment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AvailabilitySlotBookSerializer(serializers.Serializer):
    """
    Serializer for booking availability slots.
    """
    
    slot_id = serializers.IntegerField(required=True)
    patient_id = serializers.IntegerField(required=False)
    
    def validate_slot_id(self, value):
        """Validate slot exists and is available"""
        try:
            slot = AvailabilitySlot.objects.get(id=value)
            if not slot.is_available or slot.is_booked:
                raise serializers.ValidationError("Slot is not available for booking")
        except AvailabilitySlot.DoesNotExist:
            raise serializers.ValidationError("Slot does not exist")
        return value


class DoctorLeaveSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor leaves.
    """
    
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    duration_days = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorLeave
        fields = [
            'id', 'doctor', 'doctor_name', 'leave_type', 'leave_type_display',
            'start_date', 'end_date', 'duration_days', 'status', 'status_display',
            'reason', 'approved_by', 'approved_by_name', 'approval_notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_by']
    
    def get_duration_days(self, obj):
        """Get leave duration in days"""
        return obj.duration_days()
    
    def get_is_active(self, obj):
        """Check if leave is currently active"""
        return obj.is_active()
    
    def validate(self, attrs):
        """Validate leave dates"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': "End date must be after start date"
            })
        
        if start_date and start_date < timezone.now().date():
            raise serializers.ValidationError({
                'start_date': "Cannot create leave for past dates"
            })
        
        return attrs


class DoctorLeaveApprovalSerializer(serializers.Serializer):
    """
    Serializer for approving/rejecting leaves.
    """
    
    status = serializers.ChoiceField(
        choices=['APPROVED', 'REJECTED'],
        required=True
    )
    approval_notes = serializers.CharField(required=False, allow_blank=True)


class ScheduleOverrideSerializer(serializers.ModelSerializer):
    """
    Serializer for schedule overrides.
    """
    
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ScheduleOverride
        fields = [
            'id', 'doctor', 'doctor_name', 'date',
            'is_available', 'custom_start_time', 'custom_end_time',
            'reason', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def validate(self, attrs):
        """Validate override times"""
        is_available = attrs.get('is_available')
        custom_start = attrs.get('custom_start_time')
        custom_end = attrs.get('custom_end_time')
        
        if is_available and custom_start and custom_end:
            if custom_start >= custom_end:
                raise serializers.ValidationError({
                    'custom_end_time': "End time must be after start time"
                })
        
        return attrs


class DoctorAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for checking doctor availability on specific dates.
    """
    
    doctor_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, attrs):
        """Validate date range"""
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({
                'end_date': "End date must be after start date"
            })
        
        # Limit range to 30 days
        if (attrs['end_date'] - attrs['start_date']).days > 30:
            raise serializers.ValidationError("Date range cannot exceed 30 days")
        
        return attrs


class WeeklyScheduleSerializer(serializers.Serializer):
    """
    Serializer for weekly schedule view.
    """
    
    doctor_id = serializers.IntegerField(required=True)
    week_start = serializers.DateField(required=True)


class SlotGenerationSerializer(serializers.Serializer):
    """
    Serializer for generating availability slots.
    """
    
    shift_id = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    slot_duration_minutes = serializers.IntegerField(default=30, min_value=15, max_value=120)
    
    def validate(self, attrs):
        """Validate slot generation parameters"""
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({
                'end_date': "End date must be after start date"
            })
        
        # Limit to 60 days
        if (attrs['end_date'] - attrs['start_date']).days > 60:
            raise serializers.ValidationError("Cannot generate slots for more than 60 days")
        
        return attrs

class ScheduleCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Schedule Categories
    """
    total_schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduleCategory
        fields = ['id', 'name', 'description', 'total_schedules']
    
    def get_total_schedules(self, obj):
        """
        Get total number of schedules in this category
        """
        return obj.schedules.count()
    
    def validate_name(self, value):
        """
        Validate category name is unique
        """
        if ScheduleCategory.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value

class ScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for Schedules with comprehensive details
    """
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 
            'title', 
            'description', 
            'doctor', 
            'doctor_name',
            'patient', 
            'patient_name',
            'category', 
            'category_name',
            'start_time', 
            'end_time', 
            'status', 
            'priority',
            'is_recurring',
            'recurrence_pattern',
            'duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_duration(self, obj):
        """
        Calculate schedule duration
        """
        return str(obj.duration())
    
    def validate(self, data):
        """
        Validate schedule constraints
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        doctor = data.get('doctor')
        patient = data.get('patient')
        
        # Validate time constraints
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError("End time must be after start time")
            
            if start_time < timezone.now():
                raise serializers.ValidationError("Schedule cannot be in the past")
        
        # Validate doctor and patient are not the same
        if doctor and patient and doctor == patient:
            raise serializers.ValidationError("Doctor and patient cannot be the same")
        
        return data

class ScheduleReminderSerializer(serializers.ModelSerializer):
    """
    Serializer for Schedule Reminders
    """
    schedule_title = serializers.CharField(source='schedule.title', read_only=True)
    schedule_start_time = serializers.DateTimeField(source='schedule.start_time', read_only=True)
    
    class Meta:
        model = ScheduleReminder
        fields = [
            'id', 
            'schedule', 
            'schedule_title',
            'schedule_start_time',
            'reminder_type', 
            'send_time', 
            'is_sent',
            'created_at'
        ]
        read_only_fields = ['created_at', 'is_sent']
    
    def validate(self, data):
        """
        Validate reminder constraints
        """
        schedule = data.get('schedule')
        send_time = data.get('send_time')
        
        # Validate send time is before schedule start time
        if schedule and send_time:
            if send_time >= schedule.start_time:
                raise serializers.ValidationError("Reminder send time must be before schedule start time")
        
        return data