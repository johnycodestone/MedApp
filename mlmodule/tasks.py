# mlmodule/tasks.py

from celery import shared_task
from .services import MLService

@shared_task
def run_prediction_task(patient_id, model_id, input_data):
    MLService.predict(patient_id, model_id, input_data)
