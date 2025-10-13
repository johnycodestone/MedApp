from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import MLModel, Prediction
from .serializers import MLModelSerializer, PredictionSerializer
from .services import MLService

# 🔷 Class-based views for models and predictions
class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer


class PredictionViewSet(viewsets.ViewSet):
    def list(self, request):
        patient_id = request.query_params.get('patient_id')
        predictions = Prediction.objects.filter(patient_id=patient_id)
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        prediction = MLService.predict(
            patient_id=data['patient_id'],
            model_id=data['model_id'],
            input_data=data['input_data']
        )
        serializer = PredictionSerializer(prediction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 🔷 Function-based placeholder views for ML endpoints
@api_view(['POST'])
def urgency_triage_view(request):
    return Response({"message": "Urgency triage logic not implemented yet."})

@api_view(['POST'])
def diabetes_prediction_view(request):
    return Response({"message": "Symptom diagnosis logic not implemented yet."})

@api_view(['POST'])
def health_tips_view(request):
    return Response({"message": "Treatment recommendation logic not implemented yet."})

