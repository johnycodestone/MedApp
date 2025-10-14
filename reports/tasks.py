from celery import shared_task
from django.utils import timezone
from .models import Report, ReportCategory
from .services import ReportService, generate_periodic_reports
from django.db.models import Count
from .models import ReportTemplate

@shared_task
def generate_report_task(report_id, template_id=None):
    """
    Asynchronous task to generate a report
    """
    try:
        report = Report.objects.get(id=report_id)
        template = None
        
        if template_id:
            template = ReportTemplate.objects.get(id=template_id)
        
        generated_report = ReportService.generate_report(report, template)
        return {
            'report_id': generated_report.id,
            'status': generated_report.status,
            'generated_at': generated_report.generated_at
        }
    except Exception as e:
        # Log the error and mark report as failed
        report.status = Report.ReportStatus.DRAFT
        report.save()
        raise

@shared_task
def export_report_task(report_id, export_format='json'):
    """
    Asynchronous task to export a report
    """
    try:
        report = Report.objects.get(id=report_id)
        exported_file = ReportService.export_report(report, export_format)
        return {
            'report_id': report.id,
            'exported_file': exported_file,
            'export_time': timezone.now()
        }
    except Exception as e:
        # Log the error
        raise

@shared_task
def periodic_report_generation_task():
    """
    Periodic task to generate reports based on predefined schedules
    """
    generate_periodic_reports()

@shared_task
def cleanup_old_reports_task(days_old=30):
    """
    Task to clean up old reports
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
    old_reports = Report.objects.filter(
        generated_at__lt=cutoff_date,
        status=Report.ReportStatus.ARCHIVED
    )
    
    deleted_count, _ = old_reports.delete()
    
    return {
        'deleted_reports': deleted_count,
        'cutoff_date': cutoff_date
    }

@shared_task
def generate_category_summary_report(category_id):
    """
    Generate a summary report for a specific category
    """
    try:
        category = ReportCategory.objects.get(id=category_id)
        reports = Report.objects.filter(category=category)
        
        summary = {
            'category_name': category.name,
            'total_reports': reports.count(),
            'status_breakdown': list(reports.values('status').annotate(count=Count('status'))),
            'priority_breakdown': list(reports.values('priority').annotate(count=Count('priority')))
        }
        
        # Create a summary report
        summary_report = Report.objects.create(
            title=f'Summary Report for {category.name}',
            category=category,
            content=summary,
            status=Report.ReportStatus.GENERATED
        )
        
        return {
            'summary_report_id': summary_report.id,
            'total_reports': summary['total_reports']
        }
    except Exception as e:
        # Log the error
        raise
