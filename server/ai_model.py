import numpy as np
import joblib  # For loading a trained ML model

# Load pre-trained AI model (Train it separately and save as 'model.pkl')
try:
    model = joblib.load("model.pkl")
    print("AI Model Loaded Successfully!")
except Exception as e:
    print("Error loading AI model:", e)
    model = None

def predict_disease(sensor_data):
    """
    Predict possible diseases based on sensor data.
    Uses heart rate, SpO2, and temperature as input features.
    """
    if model is None:
        return "AI Model Not Available"

    # Extract relevant features
    features = np.array([[sensor_data["heart_rate"], 
                          sensor_data["spo2"], 
                          sensor_data["temperature"]]])
    
    # Predict disease
    prediction = model.predict(features)[0]

    return prediction

if __name__ == "__main__":
    # Example test case
    sample_data = {
        "heart_rate": 85,
        "spo2": 97,
        "temperature": 36.5
    }
    print("Predicted Disease:", predict_disease(sample_data))
