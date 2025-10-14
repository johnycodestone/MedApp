# Doctors App — Developer Documentation

**Purpose:** Manage doctor-related data and functions.

### Core Models
- `DoctorProfile` — doctor info
- `Timetable` — uploaded schedule files
- `Prescription` — digital prescriptions
- `AppointmentCancellation` — cancellations log

### API Endpoints
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/doctors/profile/ | GET | Retrieve doctor profile |
| /api/doctors/timetable/ | GET/POST | Upload or view timetable |
| /api/doctors/prescriptions/ | GET/POST | List or add prescriptions |
| /api/doctors/cancel-appointment/ | POST | Cancel patient appointment |

### Future Enhancements
- Link to appointments app for live schedule.
- Add doctor performance metrics & rating aggregation.
- Integrate notifications via Celery tasks.
