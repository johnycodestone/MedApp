import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from .models import Report, ReportCategory
from django.db.models import Count

def generate_report_filename(report):
    """
    Generate a standardized filename for a report
    """
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    safe_title = ''.join(c if c.isalnum() else '_' for c in report.title)
    return f"{safe_title}_{timestamp}.json"

def export_report_to_json(report):
    """
    Export a report to a JSON file
    """
    report_data = {
        'title': report.title,
        'description': report.description,
        'doctor': report.doctor.full_name if report.doctor else None,
        'patient': report.patient.full_name if report.patient else None,
        'category': report.category.name if report.category else None,
        'status': report.get_status_display(),
        'priority': report.get_priority_display(),
        'generated_at': report.generated_at,
        'published_at': report.published_at,
        'content': report.content
    }
    
    filename = generate_report_filename(report)
    
    with open(filename, 'w') as f:
        json.dump(report_data, f, cls=DjangoJSONEncoder, indent=4)
    
    return filename

def validate_report_configurations():
    """
    Validate and set up initial report configurations
    """
    # Create default report categories if they don't exist
    default_categories = [
        {
            'name': 'Medical Reports', 
            'description': 'Standard medical reports',
            'report_type': ReportCategory.ReportType.MEDICAL
        },
        {
            'name': 'Financial Reports', 
            'description': 'Financial and billing reports',
            'report_type': ReportCategory.ReportType.FINANCIAL
        },
        {
            'name': 'Operational Reports', 
            'description': 'Hospital operational reports',
            'report_type': ReportCategory.ReportType.OPERATIONAL
        }
    ]
    
    for category_data in default_categories:
        ReportCategory.objects.get_or_create(
            name=category_data['name'], 
            defaults=category_data
        )

def get_report_statistics():
    """
    Get overall report statistics
    """
    total_reports = Report.objects.count()
    status_breakdown = Report.objects.values('status').annotate(count=Count('status'))
    priority_breakdown = Report.objects.values('priority').annotate(count=Count('priority'))
    
    return {
        'total_reports': total_reports,
        'status_breakdown': list(status_breakdown),
        'priority_breakdown': list(priority_breakdown)
    }
