import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Step 1: Load Dataset
df = pd.read_csv("dataset/data.csv")  # Ensure data.csv is properly formatted

# Step 2: Define Features & Labels
X = df[["heart_rate", "spo2", "temperature"]]  # Features
y = df["disease"]  # Target label (Disease)

# Step 3: Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train Machine Learning Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Evaluate Model Accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Step 6: Save Model as 'model.pkl'
joblib.dump(model, "model.pkl")
print("Model Saved as model.pkl")



#python train_model.py
