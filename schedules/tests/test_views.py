from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from adminpanel.models import Doctor, Patient
from schedules.models import ScheduleCategory, Schedule, ScheduleReminder
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ScheduleViewsTest(TestCase):
    def setUp(self):
        """
        Set up test data for schedule views
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
        self.category = ScheduleCategory.objects.create(
            name='Medical Consultation',
            description='Regular medical consultation'
        )
        
        # Create test schedule
        self.schedule = Schedule.objects.create(
            title='Heart Check-up',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            status=Schedule.ScheduleStatus.PENDING
        )
        
        # Create test reminder
        self.reminder = ScheduleReminder.objects.create(
            schedule=self.schedule,
            reminder_type=ScheduleReminder.ReminderType.EMAIL,
            send_time=timezone.now() + timedelta(days=1),
            is_sent=False
        )
        
        # Setup API and web clients
        self.client = Client()
        self.api_client = APIClient()

    def test_schedule_dashboard_view(self):
        """
        Test schedule dashboard view access
        """
        # Test unauthenticated access
        response = self.client.get(reverse('schedule-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('schedule-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedules/dashboard.html')

    def test_schedule_calendar_view(self):
        """
        Test schedule calendar view access
        """
        # Test unauthenticated access
        response = self.client.get(reverse('schedule-calendar'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test doctor access
        self.client.login(username='doctor', password='doctorpass123')
        response = self.client.get(reverse('schedule-calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedules/calendar.html')

    def test_schedule_viewset_api(self):
        """
        Test Schedule ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('schedule-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('schedule-detail', kwargs={'pk': self.schedule.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_schedule_data = {
            'title': 'New Test Schedule',
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'category': self.category.id,
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=1)).isoformat(),
            'status': Schedule.ScheduleStatus.PENDING,
            'priority': Schedule.SchedulePriority.MEDIUM
        }
        response = self.api_client.post(reverse('schedule-list'), new_schedule_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_schedule_reminder_viewset_api(self):
        """
        Test ScheduleReminder ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('schedule-reminder-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('schedule-reminder-detail', kwargs={'pk': self.reminder.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_reminder_data = {
            'schedule': self.schedule.id,
            'reminder_type': ScheduleReminder.ReminderType.SMS,
            'send_time': (timezone.now() + timedelta(days=1)).isoformat()
        }
        response = self.api_client.post(reverse('schedule-reminder-list'), new_reminder_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_schedule_category_viewset_api(self):
        """
        Test ScheduleCategory ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('schedule-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('schedule-category-detail', kwargs={'pk': self.category.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_category_data = {
            'name': 'New Test Category',
            'description': 'A new test category for schedules'
        }
        response = self.api_client.post(reverse('schedule-category-list'), new_category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_access(self):
        """
        Test unauthorized access to schedule endpoints
        """
        # Authenticate as a non-admin user
        self.api_client.force_authenticate(user=self.patient_user)
        
        # Test create schedule (should be forbidden)
        new_schedule_data = {
            'title': 'Unauthorized Schedule',
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=1)).isoformat()
        }
        response = self.api_client.post(reverse('schedule-list'), new_schedule_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_custom_actions(self):
        """
        Test custom ViewSet actions
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test upcoming schedules
        response = self.api_client.get(reverse('upcoming-schedules'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test schedule stats
        response = self.api_client.get(reverse('schedule-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test unsent reminders
        response = self.api_client.get(reverse('unsent-reminders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
