import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

import mlflow
import mlflow.sklearn
import mlflow.models
import mlflow.models.signature

from prefect import flow, task

# Set up MLflow
#mlflow.set_tracking_uri("http://localhost:5001") #when not using docker
mlflow.set_tracking_uri("http://mlflow:5000") # This tells your train-dev container to send logs to the actual mlflow container (port 5000 internally in Docker network).
mlflow.set_experiment("CarPricePrediction")

@task
def load_data(path="./DATA/car_prices.csv"):
    return pd.read_csv(path)

@task
def preprocess_data(df):
    df = df.dropna(subset=['condition', 'sellingprice'])
    df['condition'] = df['condition'].astype(int)
    df = df[["year", "make", "condition", "odometer", "mmr", "sellingprice"]]
    df = df.dropna().drop_duplicates()

    df['make'] = df['make'].str.lower().str.strip()
    replacements = {
        'dodge tk': 'dodge', 'ford tk': 'ford', 'ford truck': 'ford',
        'gmc truck': 'gmc', 'land rover': 'landrover',
        'mercedes-benz': 'mercedes', 'mercedes-b': 'mercedes', 'vw': 'volkswagen'
    }
    df['make'] = df['make'].replace(replacements)

    for col in ['year', 'odometer', 'mmr', 'sellingprice']:
        df[col] = df[col].astype(int)

    def scale_condition(c):
        return min((c - 1) // 5 + 1, 10)
    df['condition'] = df['condition'].apply(scale_condition)

    df['make'] = df['make'].astype("category")
    df_encoded = pd.get_dummies(df, columns=['make'])
    return df_encoded

@task
def split_data(df_encoded):
    X = df_encoded.drop(columns=["sellingprice"])
    y = df_encoded["sellingprice"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

@task
def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)

    return model

@task
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Define the input signature
    print(X_test.columns.tolist())
    #input_example = X_test[["year", "condition", "odometer", "mmr", "make"]] # zou op deze manier moeten zodat je niet alle boolean encoded make_* kolommen hebt
    input_example = X_test.iloc[:1]
    signature = mlflow.models.signature.infer_signature(X_test, model.predict(X_test))

    print(f"Model Evaluation Metrics:\nMSE: {mse}\nRMSE: {rmse}\nR2: {r2}")
    return mse, rmse, r2, signature, input_example

@task
def log_to_mlflow(model, mse, rmse, r2, signature, input_example):
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)

    mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="car-price-model", signature=signature, input_example=input_example)
    print("Model logged and registered with MLflow.")

@flow(name="training-pipeline")
def training_pipeline():
    with mlflow.start_run():
        df = load_data()
        df_encoded = preprocess_data(df) 
        X_train, X_test, y_train, y_test = split_data(df_encoded)
        model = train_model(X_train, y_train)
        mse, rmse, r2, signature, input_example  = evaluate_model(model, X_test, y_test)
        log_to_mlflow(model, mse, rmse, r2, signature, input_example)
        print("Training pipeline completed successfully.")


if __name__ == "__main__":
    # Run the training pipeline 
    training_pipeline()
