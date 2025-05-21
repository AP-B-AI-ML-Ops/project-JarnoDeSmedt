import os
from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd
import mlflow

# Set MLflow tracking URI point to the MLflow server
mlflow.set_tracking_uri("http://mlflow:5000")

# Load the model from the registry (use either stage or version)
MODEL_NAME = "car-price-model"
MODEL_STAGE = "Production"  # Or use 'Staging', or 'None' if using version

app = Flask(__name__)

""" 
# Load the trained model (adjust path if needed)
with open("model.pkl", "rb") as f:
    model = pickle.load(f) 
"""
model = None  # global

try:
    #When using a version number, use model_uri parameter models:/<model_name>/<version_number>
    print(f"Loading model from: models:/{MODEL_NAME}/versions/1")
    model = mlflow.pyfunc.load_model(model_uri="models:/car-price-model/1")
    print("✅ Model loaded successfully!")

    # or with alias if you have set it in the MLflow UI
    #print(f"Loading model from: models:/{MODEL_NAME}/champion")
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/champion")

except Exception as e:
    model = None
    print(f"❌ Error loading model: {e}")

@app.route("/")
def home():
    return "ML model is running and loaded from model registry in MLFlow!"

@app.route("/predict", methods=["POST"])
def predict():
    print("DEBUG: predict endpoint called")
    print(f"DEBUG: model is type {type(model)}")
    if model is None:
        return jsonify({"error": "Model not available"}), 500
    
    data = request.get_json()
    
    # Expecting a list of features
    if not data or "features" not in data:
        return jsonify({"error": "Missing 'features' in request"}), 400

    try:
        # Expecting data["features"] to be a list of dicts
        features_df = pd.DataFrame(data["features"])
        
        print(f"DEBUG: features_df columns: {features_df.columns.tolist()}")
        print(f"DEBUG: features_df shape: {features_df.shape}")
        
        prediction = model.predict(features_df)
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)