from django.db import models
from django.contrib.auth.models import AbstractUser

# ------------------------------------------------
# Base User Model
# ------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('hospital', 'Hospital'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

# ------------------------------------------------
# Patient Model
# ------------------------------------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    blood_group = models.CharField(max_length=5)

    def __str__(self):
        return f"Patient: {self.user.username}"

# ------------------------------------------------
# Hospital Model
# ------------------------------------------------
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

# ------------------------------------------------
# Department Model
# ------------------------------------------------
class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.hospital.name})"

# ------------------------------------------------
# Doctor Model
# ------------------------------------------------
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Years of experience")

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

# ------------------------------------------------
# Appointment Model
# ------------------------------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} with {self.doctor.user.username} on {self.appointment_date}"

# ------------------------------------------------
# Prescription Model
# ------------------------------------------------
class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    medication_details = models.TextField()

    def __str__(self):
        return f"Prescription for {self.patient.user.username} ({self.appointment.id})"

# ------------------------------------------------
# Medical Record Model
# ------------------------------------------------
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    file_url = models.CharField(max_length=255)
    record_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.record_type} - {self.patient.user.username}"

# ------------------------------------------------
# Doctor Rating Model
# ------------------------------------------------
class DoctorRating(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} rated {self.doctor.user.username}"

# ------------------------------------------------
# ML Prediction Model
# ------------------------------------------------
class MLPrediction(models.Model):
    PREDICTION_TYPES = [
        ('urgency', 'Urgency Level'),
        ('diabetes', 'Diabetes Level'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPES)
    input_features = models.JSONField()  # store symptoms or input data
    predicted_value = models.CharField(max_length=100)
    probability = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prediction_type} for {self.patient.user.username}"
