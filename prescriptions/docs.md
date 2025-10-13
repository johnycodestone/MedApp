# Prescriptions App

## Purpose
Handles creation, listing, and management of prescriptions and medications between doctors and patients.

## Key Models
- `Prescription`: Links doctor, patient, and notes.
- `Medication`: Belongs to a prescription, includes dosage and frequency.

## Key Files
- `services.py`: Business logic for creating prescriptions.
- `repositories.py`: Centralized DB queries.
- `permissions.py`: Role-based access control.
- `ml_integration.py`: (Not used here, but stub if needed)

## API
- `/prescriptions/`: List prescriptions
- `/prescriptions/create/`: Create new prescription

## Tests
- Unit tests for models, services, and views in `tests/`
