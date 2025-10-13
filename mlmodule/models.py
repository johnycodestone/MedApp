# mlmodule/models.py

from django.db import models

class MLModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} v{self.version}"


class Prediction(models.Model):
    patient_id = models.IntegerField()
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    input_data = models.JSONField()
    output_data = models.JSONField()
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for Patient {self.patient_id} using {self.model}"
