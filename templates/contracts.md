# Component Contracts

Document expected template context and data attributes per component so backend/frontend agree.

## PatientCard
- Template file: templates/components/patient_card.html
- Context keys: patient (object) { id, name, age }
- Data attributes:
  - data-component="PatientCard"
  - data-props='{"id": 123, "name": "Test Patient", "age": 52}'

## Header
- Template file: templates/includes/header.html
- Context keys: user (object) { username }
- Data attributes:
  - data-component="Header"
  - data-props='{"username":"alice"}'


## Shared Components (Promoted to Root)

- `card.html`: Base layout for all entity cards (hospital, doctor, patient)
- `badge.html`: Reusable badge for verified status, support, etc.
- `stats_block.html`: KPI block for detail views
- `skeleton_card.html`: Placeholder card during loading
- CSS and JS for each component live in `static/css/components/` and `static/js/components/`
