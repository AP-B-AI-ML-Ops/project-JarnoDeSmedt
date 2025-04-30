
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

# Set up MLflow
mlflow.set_tracking_uri("http://localhost:5001")
#mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("CarPricePrediction")

def load_data(path="./DATA/car_prices.csv"):
    return pd.read_csv(path)

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

def train_and_log_model(df_encoded):
    with mlflow.start_run():
        X = df_encoded.drop(columns=["sellingprice"])
        y = df_encoded["sellingprice"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="car-price-model")
        print("Model logged and registered with MLflow.")

if __name__ == "__main__":
    df = load_data()
    df_preprocessed = preprocess_data(df)
    train_and_log_model(df_preprocessed)
