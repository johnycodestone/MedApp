# schedules/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from accounts.models import DoctorProfile, PatientProfile, HospitalProfile, AdminProfile, Department
from schedules.models import (
    ScheduleCategory, Schedule, ScheduleReminder,
    Duty, Shift, AvailabilitySlot, DoctorLeave, ScheduleOverride
)

# -------------------------------
# ScheduleCategory Tests
# -------------------------------
class ScheduleCategoryModelTest(TestCase):
    def setUp(self):
        self.category = ScheduleCategory.objects.create(
            name='Medical Consultation',
            description='Regular medical consultation schedules'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Medical Consultation')

    def test_category_str_method(self):
        self.assertEqual(str(self.category), 'Medical Consultation')

    def test_unique_category_name(self):
        with self.assertRaises(Exception):
            ScheduleCategory.objects.create(name='Medical Consultation')

# -------------------------------
# Schedule Tests
# -------------------------------
class ScheduleModelTest(TestCase):
    def setUp(self):
        self.doctor = DoctorProfile.objects.create(full_name='Dr. John Doe')
        self.patient = PatientProfile.objects.create(full_name='Jane Smith')
        self.category = ScheduleCategory.objects.create(name='Follow-up', description='Post-treatment')

        self.schedule = Schedule.objects.create(
            title='Heart Check-up',
            doctor=self.doctor,
            patient=self.patient,
            category=self.category,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            status=Schedule.ScheduleStatus.PENDING,
            priority=Schedule.SchedulePriority.MEDIUM
        )

    def test_schedule_creation(self):
        self.assertEqual(self.schedule.title, 'Heart Check-up')

    def test_schedule_str_method(self):
        self.assertTrue(str(self.schedule).startswith('Heart Check-up'))

    def test_schedule_duration(self):
        self.assertEqual(self.schedule.duration(), timedelta(hours=1))

    def test_invalid_schedule_times(self):
        with self.assertRaises(ValidationError):
            Schedule(
                title='Invalid',
                doctor=self.doctor,
                patient=self.patient,
                start_time=timezone.now() + timedelta(days=1),
                end_time=timezone.now()
            ).full_clean()

    def test_past_schedule_creation(self):
        with self.assertRaises(ValidationError):
            Schedule(
                title='Past',
                doctor=self.doctor,
                patient=self.patient,
                start_time=timezone.now() - timedelta(days=1),
                end_time=timezone.now() - timedelta(hours=23)
            ).full_clean()

# -------------------------------
# ScheduleReminder Tests
# -------------------------------
class ScheduleReminderModelTest(TestCase):
    def setUp(self):
        self.doctor = DoctorProfile.objects.create(full_name='Dr. Jane Wilson')
        self.patient = PatientProfile.objects.create(full_name='Tommy Brown')
        self.schedule = Schedule.objects.create(
            title='Vaccination',
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=7),
            end_time=timezone.now() + timedelta(days=7, hours=1)
        )
        self.reminder = ScheduleReminder.objects.create(
            schedule=self.schedule,
            reminder_type=ScheduleReminder.ReminderType.EMAIL,
            send_time=timezone.now() + timedelta(days=6),
            is_sent=False
        )

    def test_reminder_creation(self):
        self.assertEqual(self.reminder.schedule, self.schedule)

    def test_reminder_str_method(self):
        self.assertTrue(str(self.reminder).startswith('Reminder for Vaccination'))

    def test_invalid_reminder_send_time(self):
        with self.assertRaises(ValidationError):
            ScheduleReminder(
                schedule=self.schedule,
                reminder_type=ScheduleReminder.ReminderType.SMS,
                send_time=self.schedule.start_time + timedelta(hours=1)
            ).full_clean()

# -------------------------------
# Duty Tests
# -------------------------------
class DutyModelTest(TestCase):
    def setUp(self):
        self.doctor = DoctorProfile.objects.create(full_name='Dr. Duty')
        self.hospital = HospitalProfile.objects.create(hospital_name='City Hospital')
        self.department = Department.objects.create(name='Cardiology')
        self.duty = Duty.objects.create(
            doctor=self.doctor,
            hospital=self.hospital,
            department=self.department,
            duty_type='OPD',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=5),
            is_active=True
        )

    def test_duty_str(self):
        self.assertIn('OPD', str(self.duty))

    def test_is_current(self):
        self.assertTrue(self.duty.is_current())

# -------------------------------
# Shift Tests
# -------------------------------
class ShiftModelTest(TestCase):
    def setUp(self):
        self.duty = DutyModelTest.setUp(self)
        self.shift = Shift.objects.create(
            duty=self.duty,
            day_of_week=0,
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(hours=2)).time(),
            max_appointments=10
        )

    def test_shift_duration(self):
        self.assertTrue(self.shift.duration_minutes() > 0)

# -------------------------------
# AvailabilitySlot Tests
# -------------------------------
class AvailabilitySlotModelTest(TestCase):
    def setUp(self):
        self.shift = ShiftModelTest.setUp(self)
        self.slot = AvailabilitySlot.objects.create(
            shift=self.shift,
            date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timedelta(minutes=30)).time(),
            is_available=True,
            is_booked=False
        )

    def test_slot_str(self):
        self.assertIn(str(self.slot.date), str(self.slot))

# -------------------------------
# DoctorLeave Tests
# -------------------------------
class DoctorLeaveModelTest(TestCase):
    def setUp(self):
        self.doctor = DoctorProfile.objects.create(full_name='Dr. Leave')
        self.admin = AdminProfile.objects.create(full_name='Admin Approver')
        self.leave = DoctorLeave.objects.create(
            doctor=self.doctor,
            leave_type='SICK',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            status='APPROVED',
            approved_by=self.admin
        )

    def test_leave_duration(self):
        self.assertEqual(self.leave.duration_days(), 3)

    def test_is_active(self):
        self.assertTrue(self.leave.is_active())

# -------------------------------
# ScheduleOverride Tests
# -------------------------------
class ScheduleOverrideModelTest(TestCase):
    def setUp(self):
        self.doctor = DoctorProfile.objects.create(full_name='Dr. Override')
        self.admin = AdminProfile.objects.create(full_name='Admin Creator')
        self.override = ScheduleOverride.objects.create(
            doctor=self.doctor,
            date=timezone.now().date() + timedelta(days=1),
            is_available=True,
            custom_start_time=timezone.now().time(),
            custom_end_time=(timezone.now() + timedelta(hours=1)).time(),
            created_by=self.admin
        )

    def test_override_str(self):
        self.assertIn(str(self.override.date), str(self.override))
