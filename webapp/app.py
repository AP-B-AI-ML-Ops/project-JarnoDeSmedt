# this is the simple webapp to serve the model with a basic predict endpoint
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
    #when using a stage, use models:/<model_name>/<stage> Just make sure MODEL_STAGE is exactly one of:
    # "None" (literally this string, if you don't want to use a stage)
    # "Production"
    # "Staging"
    # "Archived"
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
    
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


""" 
To run the app locally , use the command: python app.py (niet nodig met docker compose want runt al vanzelf)

Send a request like this to /predict:

{
  "features": [2016, 120000, 1.6, 5, volvo]
}
=> werkt nog niet helemaal want de make column wordt geencodeerd in de model training, en geeft errors in het infer schema.

Hierdoor dus een volledige json nodig met alle makes, zoals hieronder:
{
  "features": [
    {
      "year": 2016,
      "condition": 1,
      "odometer": 120000,
      "mmr": 5000,
      "make_acura": false,
      "make_airstream": false,
      "make_aston martin": false,
      "make_audi": false,
      "make_bentley": false,
      "make_bmw": false,
      "make_buick": false,
      "make_cadillac": false,
      "make_chevrolet": false,
      "make_chrysler": false,
      "make_daewoo": false,
      "make_dodge": false,
      "make_dot": false,
      "make_ferrari": false,
      "make_fiat": false,
      "make_fisker": false,
      "make_ford": false,
      "make_geo": false,
      "make_gmc": false,
      "make_honda": false,
      "make_hummer": false,
      "make_hyundai": false,
      "make_infiniti": false,
      "make_isuzu": false,
      "make_jaguar": false,
      "make_jeep": false,
      "make_kia": false,
      "make_lamborghini": false,
      "make_landrover": false,
      "make_lexus": false,
      "make_lincoln": false,
      "make_lotus": false,
      "make_maserati": false,
      "make_mazda": false,
      "make_mercedes": false,
      "make_mercury": false,
      "make_mini": false,
      "make_mitsubishi": false,
      "make_nissan": false,
      "make_oldsmobile": false,
      "make_plymouth": false,
      "make_pontiac": false,
      "make_porsche": false,
      "make_ram": false,
      "make_rolls-royce": false,
      "make_saab": false,
      "make_saturn": false,
      "make_scion": false,
      "make_smart": false,
      "make_subaru": false,
      "make_suzuki": false,
      "make_tesla": false,
      "make_toyota": false,
      "make_volkswagen": false,
      "make_volvo": true
    }
  ]
}

"""