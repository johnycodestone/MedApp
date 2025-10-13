from django.contrib import admin
from .models import ReportCategory, Report, ReportTemplate

@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Report Categories
    """
    list_display = ('name', 'report_type', 'description')
    list_filter = ('report_type',)
    search_fields = ('name', 'description')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for Reports
    """
    list_display = (
        'title', 
        'doctor', 
        'patient', 
        'category', 
        'status', 
        'priority', 
        'generated_at'
    )
    list_filter = (
        'status', 
        'priority', 
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
    date_hierarchy = 'generated_at'
    
    readonly_fields = ('generated_at', 'updated_at', 'published_at')
    
    def get_queryset(self, request):
        """
        Optimize the queryset to reduce database queries
        """
        return super().get_queryset(request).select_related(
            'doctor', 
            'patient', 
            'category',
            'generated_by',
            'reviewed_by'
        )

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """
    Admin configuration for Report Templates
    """
    list_display = ('name', 'category', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')

# Customize admin site headers for reports
admin.site.site_header = 'Medical Reports Administration'
admin.site.site_title = 'Medical Reports Admin Portal'
admin.site.index_title = 'Welcome to Medical Reports Admin'
