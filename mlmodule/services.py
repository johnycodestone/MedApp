# mlmodule/services.py

from .repositories import MLModelRepository, PredictionRepository
import random

class MLService:
    @staticmethod
    def predict(patient_id, model_id, input_data):
        model = MLModelRepository.get_model_by_id(model_id)
        if not model:
            raise ValueError("Model not found")

        # Dummy prediction logic
        output_data = {"risk": "high" if random.random() > 0.5 else "low"}
        confidence_score = round(random.uniform(0.7, 0.99), 2)

        prediction = PredictionRepository.create_prediction(
            patient_id=patient_id,
            model=model,
            input_data=input_data,
            output_data=output_data,
            confidence_score=confidence_score
        )
        return prediction
