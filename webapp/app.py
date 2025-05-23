import mlflow
import pandas as pd
from flask import Flask, jsonify, render_template, request

MAKES = [
    "acura",
    "airstream",
    "aston martin",
    "audi",
    "bentley",
    "bmw",
    "buick",
    "cadillac",
    "chevrolet",
    "chrysler",
    "daewoo",
    "dodge",
    "dot",
    "ferrari",
    "fiat",
    "fisker",
    "ford",
    "geo",
    "gmc",
    "honda",
    "hummer",
    "hyundai",
    "infiniti",
    "isuzu",
    "jaguar",
    "jeep",
    "kia",
    "lamborghini",
    "landrover",
    "lexus",
    "lincoln",
    "lotus",
    "maserati",
    "mazda",
    "mercedes",
    "mercury",
    "mini",
    "mitsubishi",
    "nissan",
    "oldsmobile",
    "plymouth",
    "pontiac",
    "porsche",
    "ram",
    "rolls-royce",
    "saab",
    "saturn",
    "scion",
    "smart",
    "subaru",
    "suzuki",
    "tesla",
    "toyota",
    "volkswagen",
    "volvo",
]

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
    # When using a version number, models:/<model_name>/<version_number>
    print(f"Loading model from: models:/{MODEL_NAME}/versions/1")
    model = mlflow.pyfunc.load_model("models:/car-price-model/1")
    print("✅ Model loaded successfully!")

    # or with alias if you have set it in the MLflow UI
    # print(f"Loading model from: models:/{MODEL_NAME}/champion")
    # model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/champion")

except Exception as e:
    model = None
    print(f"❌ Error loading model: {e}")


@app.route("/", methods=["GET", "POST"])
def home():
    """Render the home page with a list of car makes."""
    print("ML model is running and loaded from model registry in MLFlow!")
    return render_template("index.html", makes=MAKES)


@app.route("/predict", methods=["POST"])
def predict():
    """Predict the car price based on the features provided in the request."""
    print("DEBUG: predict endpoint called")
    print(f"DEBUG: model is type {type(model)}")
    if model is None:
        return jsonify({"error": "Model not available"}), 500

    data = request.get_json()

    # Expecting a list of features
    if not data or "features" not in data:
        return jsonify({"error": "Missing 'features' in request"}), 400

    features = data.get("features")

    # Make sure condition is always float
    for feature in features:
        if "condition" in feature:
            feature["condition"] = float(feature["condition"])

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
