# mlmodule/tests/test_services.py

from django.test import TestCase
from mlmodule.models import MLModel
from mlmodule.services import MLService

class MLServiceTestCase(TestCase):
    def setUp(self):
        self.model = MLModel.objects.create(name="RiskPredictor", version="1.0", description="Predicts risk")

    def test_prediction(self):
        input_data = {"age": 45, "symptoms": ["fever", "cough"]}
        prediction = MLService.predict(patient_id=1, model_id=self.model.id, input_data=input_data)
        self.assertIn("risk", prediction.output_data)
