from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from adminpanel.models import Doctor, Patient
from reports.models import ReportCategory, Report, ReportTemplate
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ReportsViewsTest(TestCase):
    def setUp(self):
        """
        Set up test data for reports views
        """
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123'
        )
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='doctorpass123'
        )
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='patientpass123'
        )
        
        # Create test doctor and patient
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. John Doe',
            specialization='Cardiology'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='Jane Smith',
            age=35,
            gender='Female'
        )
        
        # Create test category
        self.category = ReportCategory.objects.create(
            name='Medical Consultation',
            description='Detailed medical consultation reports',
            report_type=ReportCategory.ReportType.MEDICAL
        )
        
        # Create test report
        self.report = Report.objects.create(
            title='Heart Check-up Report',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            status=Report.ReportStatus.GENERATED,
            priority=Report.ReportPriority.MEDIUM,
            generated_by=self.admin_user,
            generated_at=timezone.now() - timedelta(hours=1),
            published_at=timezone.now()
        )
        
        # Create test report template
        self.template = ReportTemplate.objects.create(
            name='Standard Medical Checkup Template',
            description='Template for standard medical checkup reports',
            template_structure={'sections': ['patient_info', 'medical_history']},
            category=self.category
        )
        
        # Setup clients
        self.client = Client()
        self.api_client = APIClient()

    def test_report_dashboard_view(self):
        """
        Test report dashboard view access
        """
        # Test unauthenticated access
        response = self.client.get(reverse('report-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('report-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/dashboard.html')

    def test_report_export_view(self):
        """
        Test report export view access
        """
        # Test unauthenticated access
        response = self.client.get(reverse('report-export'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test doctor access
        self.client.login(username='doctor', password='doctorpass123')
        response = self.client.get(reverse('report-export'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/export.html')

    def test_report_category_viewset_api(self):
        """
        Test ReportCategory ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('report-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('report-category-detail', kwargs={'pk': self.category.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_category_data = {
            'name': 'New Test Category',
            'description': 'A new test category for reports',
            'report_type': 'FINANCIAL'
        }
        response = self.api_client.post(reverse('report-category-list'), new_category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_report_viewset_api(self):
        """
        Test Report ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('report-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('report-detail', kwargs={'pk': self.report.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_report_data = {
            'title': 'New Test Report',
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'category': self.category.id,
            'status': Report.ReportStatus.DRAFT,
            'priority': Report.ReportPriority.LOW,
            'content': {'key': 'value'}
        }
        response = self.api_client.post(reverse('report-list'), new_report_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_report_template_viewset_api(self):
        """
        Test ReportTemplate ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('report-template-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('report-template-detail', kwargs={'pk': self.template.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_template_data = {
            'name': 'New Test Template',
            'description': 'A new test report template',
            'template_structure': {'sections': ['test_section']},
            'category': self.category.id
        }
        response = self.api_client.post(reverse('report-template-list'), new_template_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_access(self):
        """
        Test unauthorized access to report endpoints
        """
        # Authenticate as a non-admin user
        self.api_client.force_authenticate(user=self.patient_user)
        
        # Test create report (should be forbidden)
        new_report_data = {
            'title': 'Unauthorized Report',
            'doctor': self.doctor.id,
            'patient': self.patient.id
        }
        response = self.api_client.post(reverse('report-list'), new_report_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_custom_actions(self):
        """
        Test custom ViewSet actions
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test recent reports
        response = self.api_client.get(reverse('recent-reports'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test report stats
        response = self.api_client.get(reverse('report-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test category reports
        response = self.api_client.get(reverse('category-reports', kwargs={'pk': self.category.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test template preview
        response = self.api_client.get(reverse('template-preview', kwargs={'pk': self.template.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
