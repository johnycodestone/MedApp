from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from adminpanel.models import Doctor, Patient
from reports.models import ReportCategory, Report, ReportTemplate

User = get_user_model()

class ReportCategoryModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for ReportCategory model
        """
        self.category = ReportCategory.objects.create(
            name='Medical Consultation',
            description='Detailed medical consultation reports',
            report_type=ReportCategory.ReportType.MEDICAL
        )
    
    def test_category_creation(self):
        """
        Test ReportCategory model creation
        """
        self.assertEqual(self.category.name, 'Medical Consultation')
        self.assertEqual(self.category.report_type, ReportCategory.ReportType.MEDICAL)
    
    def test_category_str_method(self):
        """
        Test string representation of ReportCategory
        """
        self.assertEqual(str(self.category), 'Medical Consultation')
    
    def test_unique_category_name(self):
        """
        Test uniqueness of category names
        """
        with self.assertRaises(Exception):
            ReportCategory.objects.create(
                name='Medical Consultation',  # Duplicate name
                description='Another description'
            )

class ReportModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Report model
        """
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123'
        )
        
        # Create test doctor and patient
        self.doctor = Doctor.objects.create(
            full_name='Dr. John Doe',
            specialization='Cardiology'
        )
        self.patient = Patient.objects.create(
            full_name='Jane Smith',
            age=35,
            gender='Female'
        )
        
        # Create test category
        self.category = ReportCategory.objects.create(
            name='Follow-up Consultation',
            description='Post-treatment follow-up',
            report_type=ReportCategory.ReportType.MEDICAL
        )
        
        # Create a valid report
        self.report = Report.objects.create(
            title='Heart Check-up Report',
            description='Detailed heart examination report',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            content={'key': 'value'},
            status=Report.ReportStatus.GENERATED,
            priority=Report.ReportPriority.MEDIUM,
            generated_by=self.admin_user,
            generated_at=timezone.now() - timedelta(hours=1),
            published_at=timezone.now()
        )
    
    def test_report_creation(self):
        """
        Test Report model creation
        """
        self.assertEqual(self.report.title, 'Heart Check-up Report')
        self.assertEqual(self.report.doctor, self.doctor)
        self.assertEqual(self.report.patient, self.patient)
        self.assertEqual(self.report.status, Report.ReportStatus.GENERATED)
    
    def test_report_str_method(self):
        """
        Test string representation of Report
        """
        self.assertTrue(str(self.report).startswith('Heart Check-up Report'))
    
    def test_report_duration(self):
        """
        Test report generation duration calculation
        """
        duration = self.report.get_report_duration()
        self.assertIsNotNone(duration)
        self.assertTrue(duration.total_seconds() > 0)
    
    def test_invalid_report_times(self):
        """
        Test validation for invalid report times
        """
        with self.assertRaises(ValidationError):
            invalid_report = Report(
                title='Invalid Report',
                doctor=self.doctor,
                patient=self.patient,
                generated_at=timezone.now(),
                published_at=timezone.now() - timedelta(hours=1)  # Published before generation
            )
            invalid_report.full_clean()

class ReportTemplateModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for ReportTemplate model
        """
        # Create test category
        self.category = ReportCategory.objects.create(
            name='Medical Research',
            description='Research-based medical reports',
            report_type=ReportCategory.ReportType.RESEARCH
        )
        
        # Create test report template
        self.template = ReportTemplate.objects.create(
            name='Standard Medical Checkup Template',
            description='Template for standard medical checkup reports',
            template_structure={
                'sections': [
                    'patient_info',
                    'medical_history',
                    'current_examination',
                    'recommendations'
                ]
            },
            category=self.category
        )
    
    def test_template_creation(self):
        """
        Test ReportTemplate model creation
        """
        self.assertEqual(self.template.name, 'Standard Medical Checkup Template')
        self.assertEqual(self.template.category, self.category)
    
    def test_template_str_method(self):
        """
        Test string representation of ReportTemplate
        """
        self.assertEqual(str(self.template), 'Standard Medical Checkup Template')
    
    def test_unique_template_name(self):
        """
        Test uniqueness of template names
        """
        with self.assertRaises(Exception):
            ReportTemplate.objects.create(
                name='Standard Medical Checkup Template',  # Duplicate name
                description='Another description'
            )
