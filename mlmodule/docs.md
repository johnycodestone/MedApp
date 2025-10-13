# MLModule Documentation

## Overview
This app handles machine learning models and predictions for MedApp.

## Models
- `MLModel`: Stores metadata about ML models.
- `Prediction`: Stores prediction results for patients.

## API Endpoints
- `GET /api/ml/models/`
- `POST /api/ml/predictions/`

## Tasks
- `run_prediction_task`: Asynchronous prediction execution via Celery.

## Signals
- `notify_prediction_created`: Logs prediction creation.

## Permissions
- `IsMLAdmin`: Restricts access to ML admin users.
