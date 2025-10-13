# Minimal wrapper to call an ML model for symptom urgency or diabetes check
def predict_urgency(symptom_text):
    """
    Input: symptom_text (string)
    Output: dict e.g., {'urgency': 'high', 'score': 0.87}
    Implementation note: in dev, call local model; in prod, call dedicated inference service.
    """
    # Placeholder: integrate actual model later
    keywords = ['chest pain', 'breathing difficulty']
    if any(k in symptom_text.lower() for k in keywords):
        return {'urgency': 'high', 'score': 0.95}
    return {'urgency': 'low', 'score': 0.2}
