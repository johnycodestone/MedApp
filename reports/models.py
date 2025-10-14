"""
reports/models.py

Models for generating and storing various reports and analytics.
Handles system-wide reporting, statistics, and data exports.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from adminpanel.models import Doctor, Patient, Appointment, MedicalRecord, Prescription

class ReportCategory(models.Model):
    """
    Categories for different types of reports
    """
    class ReportType(models.TextChoices):
        MEDICAL = 'MEDICAL', _('Medical Report')
        FINANCIAL = 'FINANCIAL', _('Financial Report')
        OPERATIONAL = 'OPERATIONAL', _('Operational Report')
        RESEARCH = 'RESEARCH', _('Research Report')
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(
        max_length=20, 
        choices=ReportType.choices, 
        default=ReportType.MEDICAL
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Report Categories"

class Report(models.Model):
    """
    Main report model for generating various types of reports
    """
    class ReportStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        GENERATED = 'GENERATED', _('Generated')
        REVIEWED = 'REVIEWED', _('Reviewed')
        PUBLISHED = 'PUBLISHED', _('Published')
        ARCHIVED = 'ARCHIVED', _('Archived')
    
    class ReportPriority(models.IntegerChoices):
        LOW = 1, _('Low')
        MEDIUM = 2, _('Medium')
        HIGH = 3, _('High')
        CRITICAL = 4, _('Critical')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Optional relationships to other models
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reports'
    )
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reports'
    )
    
    category = models.ForeignKey(
        ReportCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reports'
    )
    
    # Report content and metadata
    content = models.JSONField(default=dict)
    raw_data = models.FileField(
        upload_to='reports/raw_data/', 
        null=True, 
        blank=True
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=ReportStatus.choices, 
        default=ReportStatus.DRAFT
    )
    
    priority = models.IntegerField(
        choices=ReportPriority.choices, 
        default=ReportPriority.MEDIUM,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ]
    )
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking and audit
    generated_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='generated_reports'
    )
    reviewed_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_reports'
    )
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_report_duration(self):
        """
        Calculate report generation duration
        """
        if self.published_at and self.generated_at:
            return self.published_at - self.generated_at
        return None
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['doctor', 'generated_at']),
            models.Index(fields=['patient', 'generated_at']),
            models.Index(fields=['status', 'generated_at'])
        ]
        verbose_name_plural = "Reports"

class ReportTemplate(models.Model):
    """
    Predefined report templates for quick report generation
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Template structure as JSON
    template_structure = models.JSONField(default=dict)
    
    # Optional category association
    category = models.ForeignKey(
        ReportCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='templates'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Report Templates"