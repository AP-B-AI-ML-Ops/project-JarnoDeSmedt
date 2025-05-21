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
#mlflow.set_tracking_uri("sqlite:///mlflow.db") # when using docker (ZIE UITLEG DOCUMENTATIE)
mlflow.set_tracking_uri("http://mlflow:5000") # This tells your train-dev container to send logs to the actual mlflow container (port 5000 internally in Docker network).
mlflow.set_experiment("CarPricePrediction")

ALL_MAKES = [
    'acura', 'airstream', 'aston martin', 'audi', 'bentley', 'bmw', 'buick',
    'cadillac', 'chevrolet', 'chrysler', 'daewoo', 'dodge', 'dot', 'ferrari',
    'fiat', 'fisker', 'ford', 'geo', 'gmc', 'honda', 'hummer', 'hyundai',
    'infiniti', 'isuzu', 'jaguar', 'jeep', 'kia', 'lamborghini', 'landrover',
    'lexus', 'lincoln', 'lotus', 'maserati', 'mazda', 'mercedes', 'mercury',
    'mini', 'mitsubishi', 'nissan', 'oldsmobile', 'plymouth', 'pontiac',
    'porsche', 'ram', 'rolls-royce', 'saab', 'saturn', 'scion', 'smart',
    'subaru', 'suzuki', 'tesla', 'toyota', 'volkswagen', 'volvo'
]

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
    
    #mlflow.log_metric("mse", mse)
    #mlflow.log_metric("rmse", rmse)
    #mlflow.log_metric("r2", r2)

    # Define the input signature
    print(X_test.columns.tolist())
    #input_example = X_test[["year", "condition", "odometer", "mmr"]]
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
        df_encoded = preprocess_data(df)  # This returns the preprocessed dataframe
        X_train, X_test, y_train, y_test = split_data(df_encoded)  # Now split it
        model = train_model(X_train, y_train)
        mse, rmse, r2, signature, input_example  = evaluate_model(model, X_test, y_test)
        log_to_mlflow(model, mse, rmse, r2, signature, input_example)
        print("Training pipeline completed successfully.")

def prepare_input(raw_input: dict, all_makes: list) -> dict:
    """
    Converts a raw car input dict to the full one-hot encoded feature dict
    required by the MLflow model.

    :param raw_input: dict with base features like 'year', 'condition', 'odometer', 'mmr', 'make'
    :param all_makes: list of all possible makes, e.g., ['audi', 'bmw', ..., 'volvo']
    :return: dict with full features including make_* booleans
    """
    # Extract base info
    year = raw_input.get("year")
    condition = raw_input.get("condition")
    odometer = raw_input.get("odometer")
    mmr = raw_input.get("mmr")
    make = raw_input.get("make", "").strip().lower()

    # One-hot encode the make
    make_features = {f"make_{m}": (m == make) for m in all_makes}

    # Merge and return the full feature set
    features = {
        "year": year,
        "condition": condition,
        "odometer": odometer,
        "mmr": mmr,
        **make_features
    }
    return features



if __name__ == "__main__":
    # Run the training pipeline 
    training_pipeline()
