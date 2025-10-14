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
