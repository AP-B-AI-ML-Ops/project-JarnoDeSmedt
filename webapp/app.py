# this is the simple webapp to serve the model with a basic predict endpoint
from flask import Flask, request, jsonify
import pickle
import numpy as np

import mlflow

# Set MLflow tracking URI (optional if running locally)
#mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_tracking_uri("http://localhost:5001")

# Load the model from the registry (use either stage or version)
MODEL_NAME = "car-price-model"
MODEL_STAGE = "Production"  # Or use 'Staging', or 'None' if using version


app = Flask(__name__)

""" 
# Load the trained model (adjust path if needed)
with open("model.pkl", "rb") as f:
    model = pickle.load(f) 
"""

try:
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
    
    # You can also load by version instead of stage:
    #print(f"Loading model from: models:/{MODEL_NAME}/versions/1")
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/versions/1")
    
    # or with alias if you have set it in the MLflow UI
    print(f"Loading model from: models:/{MODEL_NAME}/champion")
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/champion")

except Exception as e:
    model = None
    print(f"Error loading model: {e}")

@app.route("/")
def home():
    return "ML model is running and loaded from model registry in MLFlow!"

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not available"}), 500
    
    data = request.get_json()
    
    # Expecting a list of features
    if not data or "features" not in data:
        return jsonify({"error": "Missing 'features' in request"}), 400

    features = np.array(data["features"]).reshape(1, -1)

    try:
        prediction = model.predict(features)
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


""" 
To run the app, use the command: python app.py

Send a request like this to /predict:

{
  "features": [2016, 120000, 1.6, 5]
}
"""