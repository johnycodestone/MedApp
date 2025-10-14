# Hospitals App — Developer Documentation

**Purpose:** Handle all hospital-level management:
- Add/remove doctors
- Manage departments
- Assign or waive duties
- View and download reports

**API Endpoints**
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/hospitals/profile/ | POST | Register hospital |
| /api/hospitals/departments/ | POST/DELETE | Add or remove departments |
| /api/hospitals/duties/ | POST/PATCH | Assign or waive doctor duties |
| /api/hospitals/reports/ | GET | View generated reports |

**Files to edit for new features**
- Add new hospital data → `models.py`, `serializers.py`
- Add new actions → `services.py`
- Add new endpoint → `views.py`, `urls.py`
- Async task → `tasks.py`
