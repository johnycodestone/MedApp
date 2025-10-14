# Departments App — Developer Reference

**Purpose:** Manage hospital departments and their associations.

## Core Models
- Department(hospital_id, name, description, head_doctor_id)

## API Endpoints
| Endpoint | Method | Description |
|-----------|---------|-------------|
| /api/departments/ | GET | List all departments for a hospital |
| /api/departments/ | POST | Create a new department |
| /api/departments/<id>/ | PUT | Update department info |
| /api/departments/<id>/ | DELETE | Remove department |

## Typical Use Cases
- UC-HOS-03: Manage Departments
- Add/Remove/Update departments by hospital admin.

## Integration Notes
- `hospital_id` links to hospitals app.
- `head_doctor_id` links to doctors app.
- Permissions enforced via `IsHospitalOrAdmin`.

## Future Enhancements
- Add automatic head-doctor assignment.
- Integrate with doctor schedules for workload balance.
- Add department performance metrics.
