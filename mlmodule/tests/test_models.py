# mlmodule/tests/test_models.py

from django.test import TestCase
from mlmodule.models import MLModel

class MLModelTestCase(TestCase):
    def test_model_creation(self):
        model = MLModel.objects.create(name="RiskPredictor", version="1.0", description="Predicts patient risk")
        self.assertEqual(str(model), "RiskPredictor v1.0")
