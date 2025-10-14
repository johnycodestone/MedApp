# mlmodule/repositories.py

from .models import MLModel, Prediction

class MLModelRepository:
    @staticmethod
    def get_all_models():
        return MLModel.objects.all()

    @staticmethod
    def get_model_by_id(model_id):
        return MLModel.objects.filter(id=model_id).first()


class PredictionRepository:
    @staticmethod
    def get_predictions_for_patient(patient_id):
        return Prediction.objects.filter(patient_id=patient_id)

    @staticmethod
    def create_prediction(**kwargs):
        return Prediction.objects.create(**kwargs)
