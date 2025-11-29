# mlmodule/predictor.py

import torch
import numpy as np

# Load model parameters once
params = torch.load("mlmodule/triage_model.pt", map_location="cpu")

# Normalization ranges (based on training data)
mins = np.array([10, 95, 60, 80, 60, 12, 0, 0, 0, 0])
maxs = np.array([90, 105, 140, 180, 120, 30, 1, 1, 1, 1])

def normalize_features(x):
    return (x - mins) / (maxs - mins)

def forward_pass(X, params):
    theta1, bias1 = params["theta1"], params["bias1"]
    theta2, bias2 = params["theta2"], params["bias2"]
    theta3, bias3 = params["theta3"], params["bias3"]

    z1 = X @ theta1 + bias1
    a1 = torch.tanh(z1)

    z2 = a1 @ theta2 + bias2
    a2 = torch.relu(z2)

    z3 = a2 @ theta3 + bias3
    out = torch.softmax(z3, dim=1)
    return out

def predict_urgency(vitals_dict):
    """
    vitals_dict = {
        "age": 65,
        "temp": 101.2,
        "hr": 125,
        "bp_sys": 150,
        "bp_dia": 95,
        "resp_rate": 22,
        "chest_pain": 1,
        "bleeding": 0,
        "fever": 1,
        "vomiting": 0
    }
    """
    features = np.array([
        vitals_dict["age"],
        vitals_dict["temp"],
        vitals_dict["hr"],
        vitals_dict["bp_sys"],
        vitals_dict["bp_dia"],
        vitals_dict["resp_rate"],
        vitals_dict["chest_pain"],
        vitals_dict["bleeding"],
        vitals_dict["fever"],
        vitals_dict["vomiting"]
    ])

    norm = normalize_features(features)
    X = torch.tensor(norm, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        probs = forward_pass(X, params)
        pred_class = torch.argmax(probs, dim=1).item()
        class_labels = ["Low", "Medium", "High"]
        return {
            "label": class_labels[pred_class],
            "probabilities": probs.numpy().flatten().tolist()
        }
