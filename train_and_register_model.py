import json

import mlflow.models
import mlflow.models.signature
import mlflow.sklearn
import numpy as np
import pandas as pd
from evidently import Report
from evidently.metrics import *
from evidently.presets import *
from prefect import flow, task
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import mlflow

# Set up MLflow
# mlflow.set_tracking_uri("http://localhost:5001") #when not using docker
mlflow.set_tracking_uri(
    "http://mlflow:5000"
)  # This tells your train-dev container to send logs to the actual mlflow container (port 5000 internally in Docker network).
mlflow.set_experiment("CarPricePrediction")


@task(name="load-data")
def load_data(path="./DATA/car_prices.csv"):
    return pd.read_csv(path)


@task(name="preprocess-data")
def preprocess_data(df):
    df = df.dropna(subset=["condition", "sellingprice"])
    df.loc[:, "condition"] = df["condition"].astype(int)
    df = df[["year", "make", "condition", "odometer", "mmr", "sellingprice"]]
    df = df.dropna().drop_duplicates()

    df["make"] = df["make"].str.lower().str.strip()
    replacements = {
        "dodge tk": "dodge",
        "ford tk": "ford",
        "ford truck": "ford",
        "gmc truck": "gmc",
        "land rover": "landrover",
        "mercedes-benz": "mercedes",
        "mercedes-b": "mercedes",
        "vw": "volkswagen",
    }
    df["make"] = df["make"].replace(replacements)

    for col in ["year", "odometer", "mmr", "sellingprice"]:
        df[col] = df[col].astype(int)

    def scale_condition(c):
        return min((c - 1) // 5 + 1, 10)

    df.loc[:, "condition"] = df["condition"].apply(scale_condition)

    df["make"] = df["make"].astype("category")
    df_encoded = pd.get_dummies(df, columns=["make"])
    return df_encoded


@task(name="split-data")
def split_data(df_encoded):
    X = df_encoded.drop(columns=["sellingprice"])
    y = df_encoded["sellingprice"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@task(name="train-model")
def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)

    return model


@task(name="evaluate-model", log_prints=True)
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Define the input signature
    print(X_test.columns.tolist())
    # input_example = X_test[["year", "condition", "odometer", "mmr", "make"]] # zou op deze manier moeten zodat je niet alle boolean encoded make_* kolommen hebt
    input_example = X_test.iloc[:1]
    signature = mlflow.models.signature.infer_signature(X_test, model.predict(X_test))

    print(f"Model Evaluation Metrics:\nMSE: {mse}\nRMSE: {rmse}\nR2: {r2}")
    return mse, rmse, r2, signature, input_example


@task(name="log-model-to-mlflow")
def log_to_mlflow(model, mse, rmse, r2, signature, input_example):
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)

    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        registered_model_name="car-price-model",
        signature=signature,
        input_example=input_example,
    )
    print("Model logged and registered with MLflow.")


@task(name="monitor-data-drift")
def monitor_data_drift(reference_data, current_data):
    report = Report([DataDriftPreset()])

    my_eval = report.run(reference_data, current_data)
    my_eval.save_html("reports/drift_report.html")
    my_eval.save_json("reports/drift_report.json")
    print("Evidently report generated and saved as HTML.")


@task(name="check-drift-threshold", log_prints=True)
def check_drift_threshold(json_path="reports/drift_report.json", threshold=0.3):
    with open(json_path) as f:
        report = json.load(f)
        drift_score = report["metrics"][0]["value"]["dataset_drift"]

        if drift_score:
            print("⚠️ Drift detected! Triggering retraining.")
            return True
        return False


@flow(name="training-pipeline")
def training_pipeline():
    with mlflow.start_run():
        df = load_data()
        df_encoded = preprocess_data(df)
        X_train, X_test, y_train, y_test = split_data(df_encoded)
        monitor_data_drift(reference_data=X_train, current_data=X_test)

        model = train_model(X_train, y_train)
        mse, rmse, r2, signature, input_example = evaluate_model(model, X_test, y_test)
        log_to_mlflow(model, mse, rmse, r2, signature, input_example)

        print("Training pipeline completed successfully.")


if __name__ == "__main__":
    # retraining trigger after drift is detected
    # if check_drift_threshold():
    #     print("Drift detected, retraining the model.")
    #     training_pipeline()

    # Run the training pipeline
    training_pipeline()
