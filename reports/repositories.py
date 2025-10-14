from django.db.models import Q, Count
from django.utils import timezone
from .models import Report, ReportCategory, ReportTemplate

class ReportRepository:
    """
    Repository class for handling report-related database queries
    """
    @classmethod
    def get_reports_by_doctor(cls, doctor, status=None):
        """
        Get reports for a specific doctor
        """
        queryset = Report.objects.filter(doctor=doctor)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @classmethod
    def get_reports_by_patient(cls, patient, status=None):
        """
        Get reports for a specific patient
        """
        queryset = Report.objects.filter(patient=patient)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @classmethod
    def get_reports_by_category(cls, category, status=None):
        """
        Get reports for a specific category
        """
        queryset = Report.objects.filter(category=category)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @classmethod
    def get_recent_reports(cls, days=30, limit=10):
        """
        Get recent reports within a specified time frame
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        return Report.objects.filter(
            generated_at__gte=cutoff_date
        ).order_by('-generated_at')[:limit]
    
    @classmethod
    def get_reports_by_priority(cls, priority):
        """
        Get reports by priority
        """
        return Report.objects.filter(priority=priority)
    
    @classmethod
    def get_reports_statistics(cls):
        """
        Get overall report statistics
        """
        return {
            'total_reports': Report.objects.count(),
            'status_breakdown': list(Report.objects.values('status').annotate(count=Count('status'))),
            'priority_breakdown': list(Report.objects.values('priority').annotate(count=Count('priority')))
        }

class ReportTemplateRepository:
    """
    Repository class for handling report template-related database queries
    """
    @classmethod
    def get_templates_by_category(cls, category):
        """
        Get templates for a specific category
        """
        return ReportTemplate.objects.filter(category=category)
    
    @classmethod
    def get_template_by_name(cls, name):
        """
        Get a template by its name
        """
        try:
            return ReportTemplate.objects.get(name=name)
        except ReportTemplate.DoesNotExist:
            return None

class ReportCategoryRepository:
    """
    Repository class for handling report category-related database queries
    """
    @classmethod
    def get_categories_by_type(cls, report_type):
        """
        Get categories by report type
        """
        return ReportCategory.objects.filter(report_type=report_type)
    
    @classmethod
    def get_category_statistics(cls, category):
        """
        Get statistics for a specific category
        """
        reports = Report.objects.filter(category=category)
        
        return {
            'total_reports': reports.count(),
            'status_breakdown': list(reports.values('status').annotate(count=Count('status'))),
            'priority_breakdown': list(reports.values('priority').annotate(count=Count('priority')))
        }

def search_reports(query=None, doctor=None, patient=None, category=None, status=None, priority=None):
    """
    Advanced search for reports with multiple optional filters
    """
    queryset = Report.objects.all()
    
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if doctor:
        queryset = queryset.filter(doctor=doctor)
    
    if patient:
        queryset = queryset.filter(patient=patient)
    
    if category:
        queryset = queryset.filter(category=category)
    
    if status:
        queryset = queryset.filter(status=status)
    
    if priority:
        queryset = queryset.filter(priority=priority)
    
    return queryset
