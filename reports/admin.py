# reports/admin.py

from django.contrib import admin
from .models import ReportCategory, Report, ReportTemplate

# -------------------------------
# Admin registration for ReportCategory
# -------------------------------
@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for ReportCategory.
    Displays categories used to classify reports (e.g., Medical, Financial).
    """
    list_display = ('name', 'report_type', 'description')
    list_filter = ('report_type',)
    search_fields = ('name', 'description')
    ordering = ('name',)

# -------------------------------
# Admin registration for Report
# -------------------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Report.
    Displays generated reports with metadata, relationships, and status.
    Includes filters, search, and optimized queryset loading.
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
        'doctor__user__username',
        'patient__user__username'
    )
    date_hierarchy = 'generated_at'
    readonly_fields = ('generated_at', 'updated_at', 'published_at')
    ordering = ('-generated_at',)

    def get_queryset(self, request):
        """
        Optimize queryset to reduce database hits by preloading related fields.
        """
        return super().get_queryset(request).select_related(
            'doctor',
            'patient',
            'category',
            'generated_by',
            'reviewed_by'
        )

# -------------------------------
# Admin registration for ReportTemplate
# -------------------------------
@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for ReportTemplate.
    Displays reusable templates for generating reports quickly.
    """
    list_display = ('name', 'category', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

# -------------------------------
# Custom admin branding for reports
# -------------------------------
admin.site.site_header = 'Medical Reports Administration'
admin.site.site_title = 'Medical Reports Admin Portal'
admin.site.index_title = 'Welcome to Medical Reports Admin'
