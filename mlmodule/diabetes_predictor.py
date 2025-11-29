import torch
import numpy as np
import joblib
import torch.nn.functional as F

# Load artifacts
params = torch.load("mlmodule/diabetes_model.pt", map_location="cpu")
scaler = joblib.load("mlmodule/diabetes_scaler.joblib")

# Must match Diabetes.csv column order (excluding 'Class')
COLUMN_ORDER = [
    "gender", "age", "urea", "cr", "hba1c", "chol", "tg", "hdl", "ldl", "vldl", "bmi"
]


def forward_pass(x, t1, b1, t2, b2, t3, b3):
    h1 = F.relu(x @ t1 + b1)
    h2 = F.relu(h1 @ t2 + b2)
    logits = h2 @ t3 + b3
    return F.softmax(logits, dim=1)

def predict_diabetes(features_dict):
    """
    features_dict keys must match COLUMN_ORDER.
    """

    # Arrange features in the exact trained order
    row = [float(features_dict[key]) for key in COLUMN_ORDER]
    features = np.array([row], dtype=float)

    # Scale and tensorize
    scaled = scaler.transform(features)
    X = torch.tensor(scaled, dtype=torch.float32)

    with torch.no_grad():
        probs = forward_pass(
            X,
            params["d_theta1"], params["d_bias1"],
            params["d_theta2"], params["d_bias2"],
            params["d_theta3"], params["d_bias3"]
        )
        pred_class = int(torch.argmax(probs, dim=1).item())

    # TODO: Adjust labels to your actual Class mapping from the dataset
    class_labels = ["No Diabetes", "Pre-Diabetes", "Diabetes"]
    label = class_labels[pred_class]

    messages = {
        "No Diabetes": "No signs of diabetes detected. Maintain a healthy lifestyle.",
        "Pre-Diabetes": "Pre-diabetic range detected. Please consult a doctor for preventive care.",
        "Diabetes": "Diabetes detected. Medical consultation is strongly recommended."
    }

    return {"label": label, "message": messages[label]}
