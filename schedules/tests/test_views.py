# schedules/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import DoctorProfile, PatientProfile, AdminProfile, HospitalProfile, Department
from schedules.models import (
    ScheduleCategory, Schedule, ScheduleReminder,
    Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ScheduleViewsTest(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass123')
        self.doctor_user = User.objects.create_user(username='doctor', email='doctor@example.com', password='doctorpass123')
        self.patient_user = User.objects.create_user(username='patient', email='patient@example.com', password='patientpass123')

        # Create profiles
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user, full_name='Dr. John Doe')
        self.patient = PatientProfile.objects.create(user=self.patient_user, full_name='Jane Smith')
        self.admin = AdminProfile.objects.create(user=self.admin_user, full_name='Admin User')

        # Create category
        self.category = ScheduleCategory.objects.create(name='Medical Consultation', description='Regular medical consultation')

        # Create schedule
        self.schedule = Schedule.objects.create(
            title='Heart Check-up',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            status=Schedule.ScheduleStatus.PENDING
        )

        # Create reminder
        self.reminder = ScheduleReminder.objects.create(
            schedule=self.schedule,
            reminder_type=ScheduleReminder.ReminderType.EMAIL,
            send_time=timezone.now() + timedelta(hours=12),
            is_sent=False
        )

        # Create hospital and department
        self.hospital = HospitalProfile.objects.create(hospital_name='City Hospital')
        self.department = Department.objects.create(name='Cardiology')

        # Create duty
        self.duty = Duty.objects.create(
            doctor=self.doctor,
            hospital=self.hospital,
            department=self.department,
            duty_type='OPD',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            is_active=True
        )

        # Create shift
        self.shift = Shift.objects.create(
            duty=self.duty,
            day_of_week=timezone.now().weekday(),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(hours=2)).time(),
            max_appointments=10
        )

        # Create slot
        self.slot = AvailabilitySlot.objects.create(
            shift=self.shift,
            date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(minutes=30)).time()
        )

        # Create leave
        self.leave = DoctorLeave.objects.create(
            doctor=self.doctor,
            leave_type='SICK',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            status='APPROVED',
            approved_by=self.admin
        )

        # Create override
        self.override = ScheduleOverride.objects.create(
            doctor=self.doctor,
            date=timezone.now().date() + timedelta(days=1),
            is_available=True,
            custom_start_time=timezone.now().time(),
            custom_end_time=(timezone.now() + timedelta(hours=1)).time(),
            created_by=self.admin
        )

        self.client = Client()
        self.api_client = APIClient()

    def test_dashboard_and_calendar_views(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('schedule-dashboard'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='doctor', password='doctorpass123')
        response = self.client.get(reverse('schedule-calendar'))
        self.assertEqual(response.status_code, 200)

    def test_schedule_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('schedule-list'))
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get(reverse('schedule-detail', kwargs={'pk': self.schedule.id}))
        self.assertEqual(response.status_code, 200)

    def test_reminder_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('schedule-reminder-list'))
        self.assertEqual(response.status_code, 200)

    def test_category_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('schedule-category-list'))
        self.assertEqual(response.status_code, 200)

    def test_duty_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('duty-list'))
        self.assertEqual(response.status_code, 200)

    def test_shift_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('shift-list'))
        self.assertEqual(response.status_code, 200)

    def test_slot_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('availability-slot-list'))
        self.assertEqual(response.status_code, 200)

    def test_leave_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('doctor-leave-list'))
        self.assertEqual(response.status_code, 200)

    def test_override_api(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.get(reverse('schedule-override-list'))
        self.assertEqual(response.status_code, 200)

    def test_custom_actions(self):
        self.api_client.force_authenticate(user=self.admin_user)
        self.assertEqual(self.api_client.get(reverse('upcoming-schedules')).status_code, 200)
        self.assertEqual(self.api_client.get(reverse('schedule-stats')).status_code, 200)
        self.assertEqual(self.api_client.get(reverse('unsent-reminders')).status_code, 200)

    def test_unauthorized_schedule_creation(self):
        self.api_client.force_authenticate(user=self.patient_user)
        response = self.api_client.post(reverse('schedule-list'), {
            'title': 'Unauthorized',
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=1)).isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
