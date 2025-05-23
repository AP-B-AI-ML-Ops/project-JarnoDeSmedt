import pandas as pd

ALL_MAKES = [
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


def predict_price(model, raw_input: dict) -> float:
    """
    Predicts the price of a car based on the input features.

    :param model: The trained MLflow model
    :param raw_input: dict with base features like 'year', 'condition', 'odometer', 'mmr', 'make'
    :return: predicted price
    """
    # Prepare the input data
    all_makes = ALL_MAKES
    input_data = prepare_input(raw_input, all_makes)

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])

    # Make prediction
    prediction = model.predict(input_df)

    return prediction[0]


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
        **make_features,
    }
    return features
