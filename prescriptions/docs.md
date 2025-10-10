# prescriptions app — Developer docs

## Overview
Manages prescriptions (create, list, update), medications tied to prescriptions, PDF generation, and storage.

## Key models
- `Prescription` — patient, doctor, notes, file, status (draft|final|revoked), summary
- `Medication` — prescription FK, name, dosage, frequency, duration, quantity, instructions

## API
Register router:
```py
# project urls.py
path("api/", include("prescriptions.urls")),
