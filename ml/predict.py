import os
import math
import joblib
import pandas as pd


# -----------------------------
# MODEL FILE PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REG_MODEL_FILE = os.path.join(BASE_DIR, "sales_model.pkl")
CLS_MODEL_FILE = os.path.join(BASE_DIR, "sales_classifier.pkl")


# -----------------------------
# LOAD MODEL
# -----------------------------
def load_model(path):
    """
    Loads a saved pickle/joblib model.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")

    return joblib.load(path)


# -----------------------------
# SAFE NUMERIC CONVERSION
# -----------------------------
def safe_float(value, default=0.0):
    """
    Converts input value to float safely.
    If value is missing or invalid, default value is used.
    """

    try:
        if value is None:
            return default

        return float(value)

    except Exception:
        return default


# -----------------------------
# PREPARE INPUT FOR MODEL
# -----------------------------
def prepare_input_for_model(input_data, model):
    """
    Creates a single-row DataFrame for prediction.

    If the model was trained with specific feature columns,
    this function aligns the input columns with model.feature_names_in_.
    This prevents crash due to extra or missing fields.
    """

    df = pd.DataFrame([input_data])

    model_features = getattr(model, "feature_names_in_", None)

    if model_features is not None:
        for column in model_features:
            if column not in df.columns:
                df[column] = 0

        df = df[list(model_features)]

    return df


# -----------------------------
# PREDICTION FUNCTION
# -----------------------------
def predict_sales(**kwargs):
    """
    Predicts sales amount and sales class.

    This function accepts flexible keyword arguments from FastAPI payload,
    including product_id, category, region, quantity, discount, etc.
    """

    regression_model = load_model(REG_MODEL_FILE)
    classification_model = load_model(CLS_MODEL_FILE)

    input_data = {
        "product_id": kwargs.get("product_id", "UNKNOWN"),
        "ship_mode": kwargs.get("ship_mode", "Standard Class"),
        "segment": kwargs.get("segment", "Consumer"),
        "state": kwargs.get("state", "Unknown"),
        "country": kwargs.get("country", "Unknown"),
        "market": kwargs.get("market", "Unknown"),
        "region": kwargs.get("region", "Unknown"),
        "category": kwargs.get("category", "Unknown"),
        "sub_category": kwargs.get("sub_category", "Unknown"),
        "order_priority": kwargs.get("order_priority", "Medium"),

        "quantity": safe_float(kwargs.get("quantity")),
        "discount": safe_float(kwargs.get("discount")),
        "profit": safe_float(kwargs.get("profit")),
        "shipping_cost": safe_float(kwargs.get("shipping_cost")),
        "ship_days": safe_float(kwargs.get("ship_days")),
        "order_month": safe_float(kwargs.get("order_month")),
        "order_year": safe_float(kwargs.get("order_year")),
        "profit_margin": safe_float(kwargs.get("profit_margin")),
    }

    regression_input = prepare_input_for_model(input_data, regression_model)
    classification_input = prepare_input_for_model(input_data, classification_model)

    predicted_sales = regression_model.predict(regression_input)[0]

    # If regression model was trained using log1p target,
    # small prediction values may be in log scale.
    if predicted_sales < 20:
        predicted_sales = math.expm1(predicted_sales)

    predicted_sales = round(float(predicted_sales), 2)

    predicted_class = classification_model.predict(classification_input)[0]
    predicted_class = str(predicted_class)

    return {
        "predicted_sales": predicted_sales,

        # Required by pytest
        "predicted_sales_class": predicted_class,

        # Kept for readable Swagger output
        "sales_class": predicted_class,

        "model_files": {
            "regression_model": "ml/sales_model.pkl",
            "classification_model": "ml/sales_classifier.pkl"
        },

        "input_used": input_data
    }