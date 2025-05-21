import sys
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train_and_register_model import load_data, preprocess_data, split_data, evaluate_model, train_model

def test_load_data():
    #df = load_data() # ❌ Will not return data — it's a Prefect task
    df = load_data.fn() # use .fn to call the individual prefect tasks outside the flow
    assert not df.empty
    assert "sellingprice" in df.columns

def test_preprocess_data():
    df = load_data.fn()
    df_pre = preprocess_data.fn(df)
    assert "sellingprice" in df_pre.columns
    assert df_pre.isnull().sum().sum() == 0

def test_split_data():
    df = load_data.fn()
    df_pre = preprocess_data.fn(df)
    X_train, X_test, y_train, y_test = split_data.fn(df_pre)
    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(X_train) + len(X_test) == len(df_pre)

def test_evaluate_model():
    # Create mock data similar to post-preprocessing format
    data = {
        "year": [2010, 2011],
        "odometer": [80000, 70000],
        "mmr": [10000, 10500],
        "condition": [5, 6],
        "sellingprice": [9500, 9800],
        "make_toyota": [1, 0],
        "make_ford": [0, 1]
    }
    df = pd.DataFrame(data)

    X = df.drop(columns=["sellingprice"])
    y = df["sellingprice"]

    model = LinearRegression()
    model.fit(X, y)

    mse, rmse, r2, signature, input_example = evaluate_model.fn(model, X, y)

    assert mse >= 0
    assert rmse >= 0
    assert -1 <= r2 <= 1
    assert signature is not None
    assert input_example is not None