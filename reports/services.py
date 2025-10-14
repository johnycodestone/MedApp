from django.utils import timezone
from django.db import transaction
from .models import Report, ReportCategory, ReportTemplate
from .utils import export_report_to_json

class ReportService:
    """
    Service class for handling report-related operations
    """
    @classmethod
    @transaction.atomic
    def create_report(cls, title, doctor=None, patient=None, category=None, content=None, generated_by=None):
        """
        Create a new report with optional parameters
        """
        report = Report.objects.create(
            title=title,
            doctor=doctor,
            patient=patient,
            category=category,
            content=content or {},
            generated_by=generated_by,
            status=Report.ReportStatus.DRAFT
        )
        return report
    
    @classmethod
    @transaction.atomic
    def generate_report(cls, report, template=None):
        """
        Generate a report using an optional template
        """
        if template:
            # Apply template structure to report content
            report.content.update(template.template_structure)
        
        report.status = Report.ReportStatus.GENERATED
        report.published_at = timezone.now()
        report.save()
        
        return report
    
    @classmethod
    def export_report(cls, report, export_format='json'):
        """
        Export a report to a specific format
        """
        if export_format == 'json':
            return export_report_to_json(report)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

class ReportTemplateService:
    """
    Service class for handling report template operations
    """
    @classmethod
    @transaction.atomic
    def create_template(cls, name, template_structure, category=None, description=None):
        """
        Create a new report template
        """
        template = ReportTemplate.objects.create(
            name=name,
            template_structure=template_structure,
            category=category,
            description=description
        )
        return template
    
    @classmethod
    def get_template_by_category(cls, category):
        """
        Get templates for a specific category
        """
        return ReportTemplate.objects.filter(category=category)

class ReportCategoryService:
    """
    Service class for handling report category operations
    """
    @classmethod
    @transaction.atomic
    def create_category(cls, name, report_type, description=None):
        """
        Create a new report category
        """
        category = ReportCategory.objects.create(
            name=name,
            report_type=report_type,
            description=description
        )
        return category
    
    @classmethod
    def get_categories_by_type(cls, report_type):
        """
        Get categories by report type
        """
        return ReportCategory.objects.filter(report_type=report_type)

def generate_periodic_reports():
    """
    Generate periodic reports based on predefined templates and categories
    """
    # Implement logic for generating periodic reports
    # This could involve checking for due reports, applying templates, etc.
    pass
