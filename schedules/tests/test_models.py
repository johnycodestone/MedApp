from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from adminpanel.models import Doctor, Patient  # Assuming these are imported from adminpanel
from schedules.models import ScheduleCategory, Schedule, ScheduleReminder

class ScheduleCategoryModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for ScheduleCategory model
        """
        self.category = ScheduleCategory.objects.create(
            name='Medical Consultation',
            description='Regular medical consultation schedules'
        )
    
    def test_category_creation(self):
        """
        Test ScheduleCategory model creation
        """
        self.assertEqual(self.category.name, 'Medical Consultation')
        self.assertEqual(self.category.description, 'Regular medical consultation schedules')
    
    def test_category_str_method(self):
        """
        Test string representation of ScheduleCategory
        """
        self.assertEqual(str(self.category), 'Medical Consultation')
    
    def test_unique_category_name(self):
        """
        Test uniqueness of category names
        """
        with self.assertRaises(Exception):
            ScheduleCategory.objects.create(
                name='Medical Consultation',  # Duplicate name
                description='Another description'
            )

class ScheduleModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Schedule model
        """
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
        self.category = ScheduleCategory.objects.create(
            name='Follow-up Consultation',
            description='Post-treatment follow-up'
        )
        
        # Create a valid schedule
        self.schedule = Schedule.objects.create(
            title='Heart Check-up',
            description='Routine heart examination',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            status=Schedule.ScheduleStatus.PENDING,
            priority=Schedule.SchedulePriority.MEDIUM
        )
    
    def test_schedule_creation(self):
        """
        Test Schedule model creation
        """
        self.assertEqual(self.schedule.title, 'Heart Check-up')
        self.assertEqual(self.schedule.doctor, self.doctor)
        self.assertEqual(self.schedule.patient, self.patient)
        self.assertEqual(self.schedule.status, Schedule.ScheduleStatus.PENDING)
    
    def test_schedule_str_method(self):
        """
        Test string representation of Schedule
        """
        self.assertTrue(str(self.schedule).startswith('Heart Check-up'))
    
    def test_schedule_duration(self):
        """
        Test schedule duration calculation
        """
        expected_duration = timedelta(hours=1)
        self.assertEqual(self.schedule.duration(), expected_duration)
    
    def test_invalid_schedule_times(self):
        """
        Test validation for invalid schedule times
        """
        with self.assertRaises(ValidationError):
            invalid_schedule = Schedule(
                title='Invalid Schedule',
                doctor=self.doctor,
                patient=self.patient,
                start_time=timezone.now() + timedelta(days=1),
                end_time=timezone.now()  # End time before start time
            )
            invalid_schedule.full_clean()
    
    def test_past_schedule_creation(self):
        """
        Test prevention of creating schedules in the past
        """
        with self.assertRaises(ValidationError):
            past_schedule = Schedule(
                title='Past Schedule',
                doctor=self.doctor,
                patient=self.patient,
                start_time=timezone.now() - timedelta(days=1),
                end_time=timezone.now() - timedelta(hours=23)
            )
            past_schedule.full_clean()

class ScheduleReminderModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for ScheduleReminder model
        """
        # Create test doctor and patient
        self.doctor = Doctor.objects.create(
            full_name='Dr. Jane Wilson',
            specialization='Pediatrics'
        )
        self.patient = Patient.objects.create(
            full_name='Tommy Brown',
            age=8,
            gender='Male'
        )
        
        # Create test schedule
        self.schedule = Schedule.objects.create(
            title='Child Vaccination',
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=7),
            end_time=timezone.now() + timedelta(days=7, hours=1)
        )
        
        # Create schedule reminder
        self.reminder = ScheduleReminder.objects.create(
            schedule=self.schedule,
            reminder_type=ScheduleReminder.ReminderType.EMAIL,
            send_time=timezone.now() + timedelta(days=6),
            is_sent=False
        )
    
    def test_reminder_creation(self):
        """
        Test ScheduleReminder model creation
        """
        self.assertEqual(self.reminder.schedule, self.schedule)
        self.assertEqual(self.reminder.reminder_type, ScheduleReminder.ReminderType.EMAIL)
        self.assertFalse(self.reminder.is_sent)
    
    def test_reminder_str_method(self):
        """
        Test string representation of ScheduleReminder
        """
        self.assertTrue(str(self.reminder).startswith('Reminder for Child Vaccination'))
    
    def test_invalid_reminder_send_time(self):
        """
        Test validation for reminder send time
        """
        with self.assertRaises(ValidationError):
            invalid_reminder = ScheduleReminder(
                schedule=self.schedule,
                reminder_type=ScheduleReminder.ReminderType.SMS,
                send_time=self.schedule.start_time + timedelta(hours=1)  # Send time after schedule start
            )
            invalid_reminder.full_clean()
