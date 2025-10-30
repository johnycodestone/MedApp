# schedules/admin.py

from django.contrib import admin
from .models import (
    ScheduleCategory,
    Schedule,
    ScheduleReminder,
    Duty,
    Shift,
    AvailabilitySlot,
    DoctorLeave,
    ScheduleOverride
)

# -------------------------------
# Schedule Category Admin
# -------------------------------
@admin.register(ScheduleCategory)
class ScheduleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

# -------------------------------
# Schedule Admin
# -------------------------------
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'doctor', 'patient', 'start_time',
        'end_time', 'status', 'priority'
    )
    list_filter = (
        'status', 'priority', 'is_recurring', 'category',
        ('doctor', admin.RelatedOnlyFieldListFilter),
        ('patient', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'title', 'description',
        'doctor__full_name', 'patient__full_name'
    )
    date_hierarchy = 'start_time'
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor', 'patient', 'category')

# -------------------------------
# Schedule Reminder Admin
# -------------------------------
@admin.register(ScheduleReminder)
class ScheduleReminderAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'reminder_type', 'send_time', 'is_sent')
    list_filter = ('reminder_type', 'is_sent')
    search_fields = (
        'schedule__title',
        'schedule__doctor__full_name',
        'schedule__patient__full_name'
    )
    date_hierarchy = 'send_time'
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('schedule')

# -------------------------------
# Duty Admin
# -------------------------------
@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'hospital', 'duty_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('duty_type', 'is_active', 'hospital')
    search_fields = ('doctor__user__username', 'hospital__hospital_name', 'notes')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')

# -------------------------------
# Shift Admin
# -------------------------------
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('duty', 'day_of_week', 'start_time', 'end_time', 'max_appointments', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('duty__doctor__user__username',)
    readonly_fields = ('created_at', 'updated_at')

# -------------------------------
# Availability Slot Admin
# -------------------------------
@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('shift', 'date', 'start_time', 'end_time', 'is_available', 'is_booked')
    list_filter = ('is_available', 'is_booked', 'date')
    search_fields = ('shift__duty__doctor__user__username',)
    readonly_fields = ('created_at', 'updated_at')

# -------------------------------
# Doctor Leave Admin
# -------------------------------
@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('leave_type', 'status')
    search_fields = ('doctor__user__username', 'reason')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')

# -------------------------------
# Schedule Override Admin
# -------------------------------
@admin.register(ScheduleOverride)
class ScheduleOverrideAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'is_available', 'custom_start_time', 'custom_end_time')
    list_filter = ('is_available', 'date')
    search_fields = ('doctor__user__username', 'reason')
    readonly_fields = ('created_at', 'updated_at')

# -------------------------------
# Custom Admin Branding
# -------------------------------
admin.site.site_header = 'Medical Schedules Administration'
admin.site.site_title = 'Medical Schedules Admin Portal'
admin.site.index_title = 'Welcome to Medical Schedules Admin'
