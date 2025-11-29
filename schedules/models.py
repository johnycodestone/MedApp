# schedules/models.py

"""
Models for managing doctor schedules, duties, shifts, availability, and overrides.
Supports hospital-assigned duties and doctor-driven availability.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import DoctorProfile, PatientProfile, HospitalProfile, Department
#kdk

# -------------------------------
# Schedule Categories
# -------------------------------
class ScheduleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Schedule Categories"


# -------------------------------
# Hospital-Assigned Duties
# -------------------------------
class Duty(models.Model):
    class DutyType(models.TextChoices):
        OPD = 'OPD', _('Outpatient Duty')
        IPD = 'IPD', _('Inpatient Duty')
        EMERGENCY = 'EMERGENCY', _('Emergency Duty')
        ADMIN = 'ADMIN', _('Administrative Duty')

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='duties')
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='duties')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    duty_type = models.CharField(max_length=20, choices=DutyType.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_current(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today and (not self.end_date or today <= self.end_date)

    def __str__(self):
        return f"{self.doctor} - {self.duty_type} ({self.start_date})"


# -------------------------------
# Shifts Assigned to Duties
# -------------------------------
class Shift(models.Model):
    duty = models.ForeignKey(Duty, on_delete=models.CASCADE, related_name='shifts')

    day_of_week = models.IntegerField(
        choices=[(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])],
        help_text="0 = Monday, 6 = Sunday"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_appointments = models.PositiveIntegerField(default=10)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def duration_minutes(self):
        start = datetime.combine(timezone.now().date(), self.start_time)
        end = datetime.combine(timezone.now().date(), self.end_time)
        return int((end - start).total_seconds() / 60)

    def __str__(self):
        return f"{self.duty} - {self.get_day_of_week_display()}"


# -------------------------------
# Availability Slots for Booking
# -------------------------------
class AvailabilitySlot(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)

    booked_by = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shift} - {self.date} {self.start_time}"


# -------------------------------
# Doctor Leave Requests
# -------------------------------
class DoctorLeave(models.Model):
    class LeaveType(models.TextChoices):
        SICK = 'SICK', _('Sick Leave')
        VACATION = 'VACATION', _('Vacation')
        EMERGENCY = 'EMERGENCY', _('Emergency Leave')

    class LeaveStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)
    approved_by = models.ForeignKey('accounts.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True)
    approval_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    def is_active(self):
        today = timezone.now().date()
        return self.status == 'APPROVED' and self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.doctor} - {self.leave_type} ({self.start_date})"


# -------------------------------
# Schedule Overrides by Doctor
# -------------------------------
class ScheduleOverride(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='overrides')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    custom_start_time = models.TimeField(null=True, blank=True)
    custom_end_time = models.TimeField(null=True, blank=True)
    reason = models.TextField(blank=True)

    created_by = models.ForeignKey('accounts.AdminProfile', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.doctor} override on {self.date}"


# -------------------------------
# Patient-Facing Schedule Entries
# -------------------------------
class Schedule(models.Model):
    class ScheduleStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    class SchedulePriority(models.IntegerChoices):
        LOW = 1, _('Low')
        MEDIUM = 2, _('Medium')
        HIGH = 3, _('High')
        URGENT = 4, _('Urgent')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='schedules')
    category = models.ForeignKey(ScheduleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ScheduleStatus.choices, default=ScheduleStatus.PENDING)
    priority = models.IntegerField(choices=SchedulePriority.choices, default=SchedulePriority.MEDIUM)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return f"{self.title} - {self.start_time}"

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['doctor', 'start_time']),
            models.Index(fields=['patient', 'start_time']),
            models.Index(fields=['status', 'start_time']),
        ]


# -------------------------------
# Schedule Reminders
# -------------------------------
class ScheduleReminder(models.Model):
    class ReminderType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        PUSH = 'PUSH', _('Push Notification')

    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, related_name='reminder')
    reminder_type = models.CharField(max_length=10, choices=ReminderType.choices, default=ReminderType.EMAIL)
    send_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.schedule.title}"

    class Meta:
        ordering = ['-send_time']
