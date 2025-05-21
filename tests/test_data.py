import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train_and_register_model import load_data, preprocess_data

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
