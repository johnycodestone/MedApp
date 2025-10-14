"""
schedules/models.py

Models for managing doctor schedules, availability, duties, and shifts.
Handles time management for doctors and hospitals.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from adminpanel.models import Doctor, Patient  # Assuming these are imported from adminpanel

class ScheduleCategory(models.Model):
    """
    Categories for different types of schedules
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Schedule Categories"

class Schedule(models.Model):
    """
    Main schedule model for managing various scheduling needs
    """
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
    
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name=_('Assigned Doctor')
    )
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name=_('Related Patient')
    )
    
    category = models.ForeignKey(
        ScheduleCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='schedules'
    )
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(
        max_length=20, 
        choices=ScheduleStatus.choices, 
        default=ScheduleStatus.PENDING
    )
    
    priority = models.IntegerField(
        choices=SchedulePriority.choices, 
        default=SchedulePriority.MEDIUM,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ]
    )
    
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.start_time}"
    
    def duration(self):
        """
        Calculate the duration of the schedule
        """
        return self.end_time - self.start_time
    
    class Meta:
        ordering = ['-start_time']
        verbose_name_plural = "Schedules"
        indexes = [
            models.Index(fields=['doctor', 'start_time']),
            models.Index(fields=['patient', 'start_time']),
            models.Index(fields=['status', 'start_time'])
        ]

class ScheduleReminder(models.Model):
    """
    Reminders associated with schedules
    """
    class ReminderType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        PUSH = 'PUSH', _('Push Notification')
    
    schedule = models.OneToOneField(
        Schedule, 
        on_delete=models.CASCADE, 
        related_name='reminder'
    )
    
    reminder_type = models.CharField(
        max_length=10, 
        choices=ReminderType.choices, 
        default=ReminderType.EMAIL
    )
    
    send_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.schedule.title}"
    
    class Meta:
        ordering = ['-send_time']