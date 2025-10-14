# mlmodule/tests/test_views.py

from rest_framework.test import APITestCase
from mlmodule.models import MLModel

class PredictionViewTestCase(APITestCase):
    def setUp(self):
        self.model = MLModel.objects.create(name="RiskPredictor", version="1.0", description="Predicts risk")

    def test_create_prediction(self):
        response = self.client.post("/api/ml/predictions/", {
            "patient_id": 1,
            "model_id": self.model.id,
            "input_data": {"age": 45, "symptoms": ["fever"]}
        }, format='json')
        self.assertEqual(response.status_code, 201)
