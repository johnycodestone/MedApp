from django.contrib import admin
from .models import ScheduleCategory, Schedule, ScheduleReminder

@admin.register(ScheduleCategory)
class ScheduleCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Schedule Categories
    """
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Schedules
    """
    list_display = (
        'title', 
        'doctor', 
        'patient', 
        'start_time', 
        'end_time', 
        'status', 
        'priority'
    )
    list_filter = (
        'status', 
        'priority', 
        'is_recurring', 
        'category',
        ('doctor', admin.RelatedOnlyFieldListFilter),
        ('patient', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'title', 
        'description', 
        'doctor__full_name', 
        'patient__full_name'
    )
    date_hierarchy = 'start_time'
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """
        Optimize the queryset to reduce database queries
        """
        return super().get_queryset(request).select_related(
            'doctor', 
            'patient', 
            'category'
        )

@admin.register(ScheduleReminder)
class ScheduleReminderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Schedule Reminders
    """
    list_display = (
        'schedule', 
        'reminder_type', 
        'send_time', 
        'is_sent'
    )
    list_filter = (
        'reminder_type', 
        'is_sent'
    )
    search_fields = (
        'schedule__title', 
        'schedule__doctor__full_name', 
        'schedule__patient__full_name'
    )
    date_hierarchy = 'send_time'
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """
        Optimize the queryset to reduce database queries
        """
        return super().get_queryset(request).select_related('schedule')

# Customize admin site headers for schedules
admin.site.site_header = 'Medical Schedules Administration'
admin.site.site_title = 'Medical Schedules Admin Portal'
admin.site.index_title = 'Welcome to Medical Schedules Admin'
