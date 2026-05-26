import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_FILE = Path("data/processed/retail_orders_clean.csv")

REG_MODEL_FILE = Path("ml/sales_model.pkl")
CLS_MODEL_FILE = Path("ml/sales_classifier.pkl")
METRICS_FILE = Path("ml/model_metrics.txt")


def main():
    df = pd.read_csv(DATA_FILE)

    # =========================
    # TARGET COLUMNS
    # =========================
    y_reg = df["sales"]
    y_cls = df["sales_class"]

    # =========================
    # REGRESSION FEATURES
    # =========================
    # Regression predicts actual sales amount.
    # product_id is useful here because product-level sales behavior matters.
    regression_features = [
        "product_id",
        "ship_mode",
        "segment",
        "state",
        "country",
        "market",
        "region",
        "category",
        "sub_category",
        "order_priority",
        "quantity",
        "discount",
        "profit",
        "shipping_cost",
        "ship_days",
        "order_month",
        "order_year",
        "profit_margin",
    ]

    regression_categorical = [
        "product_id",
        "ship_mode",
        "segment",
        "state",
        "country",
        "market",
        "region",
        "category",
        "sub_category",
        "order_priority",
    ]

    regression_numeric = [
        "quantity",
        "discount",
        "profit",
        "shipping_cost",
        "ship_days",
        "order_month",
        "order_year",
        "profit_margin",
    ]

    # =========================
    # CLASSIFICATION FEATURES
    # =========================
    # Classification predicts Low / Medium / High sales class.
    # product_id is removed here because it was hurting generalization.
    classification_features = [
        "ship_mode",
        "segment",
        "state",
        "country",
        "market",
        "region",
        "category",
        "sub_category",
        "order_priority",
        "quantity",
        "discount",
        "profit",
        "shipping_cost",
        "ship_days",
        "order_month",
        "order_year",
        "profit_margin",
    ]

    classification_categorical = [
        "ship_mode",
        "segment",
        "state",
        "country",
        "market",
        "region",
        "category",
        "sub_category",
        "order_priority",
    ]

    classification_numeric = [
        "quantity",
        "discount",
        "profit",
        "shipping_cost",
        "ship_days",
        "order_month",
        "order_year",
        "profit_margin",
    ]

    X_reg = df[regression_features]
    X_cls = df[classification_features]

    # Same train-test split index for both regression and classification
    train_idx, test_idx = train_test_split(
        df.index,
        test_size=0.2,
        random_state=42,
        stratify=y_cls
    )

    X_reg_train = X_reg.loc[train_idx]
    X_reg_test = X_reg.loc[test_idx]

    X_cls_train = X_cls.loc[train_idx]
    X_cls_test = X_cls.loc[test_idx]

    y_reg_train = y_reg.loc[train_idx]
    y_reg_test = y_reg.loc[test_idx]

    y_cls_train = y_cls.loc[train_idx]
    y_cls_test = y_cls.loc[test_idx]

    # =========================
    # PREPROCESSORS
    # =========================

    regression_preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), regression_categorical),
            ("num", "passthrough", regression_numeric),
        ]
    )

    classification_preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), classification_categorical),
            ("num", "passthrough", classification_numeric),
        ]
    )

    # =========================
    # REGRESSION MODEL
    # =========================
    # ExtraTrees improves sales prediction.
    # Parameters are controlled to keep train/test score in a practical range.
    base_regressor = ExtraTreesRegressor(
        n_estimators=350,
        max_depth=11,
        min_samples_split=18,
        min_samples_leaf=8,
        max_features=0.65,
        random_state=42,
        n_jobs=-1,
    )

    regression_model = Pipeline(
        steps=[
            ("preprocessor", regression_preprocessor),
            (
                "model",
                TransformedTargetRegressor(
                    regressor=base_regressor,
                    func=np.log1p,
                    inverse_func=np.expm1
                )
            ),
        ]
    )

    # =========================
    # CLASSIFICATION MODEL
    # =========================
    # class_weight removed because it was over-predicting High class.
    # This should improve overall classification accuracy.
    classification_model = Pipeline(
        steps=[
            ("preprocessor", classification_preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=500,
                    max_depth=11,
                    min_samples_split=18,
                    min_samples_leaf=7,
                    max_features=0.65,
                    class_weight=None,
                    random_state=42,
                    n_jobs=-1,
                )
            ),
        ]
    )
    # =========================
    # TRAINING
    # =========================

    regression_model.fit(X_reg_train, y_reg_train)
    classification_model.fit(X_cls_train, y_cls_train)

    # =========================
    # PREDICTIONS
    # =========================

    reg_train_pred = regression_model.predict(X_reg_train)
    reg_test_pred = regression_model.predict(X_reg_test)

    cls_train_pred = classification_model.predict(X_cls_train)
    cls_test_pred = classification_model.predict(X_cls_test)

    # =========================
    # REGRESSION METRICS
    # =========================

    train_r2 = r2_score(y_reg_train, reg_train_pred)
    test_r2 = r2_score(y_reg_test, reg_test_pred)

    train_mae = mean_absolute_error(y_reg_train, reg_train_pred)
    test_mae = mean_absolute_error(y_reg_test, reg_test_pred)

    train_rmse = np.sqrt(mean_squared_error(y_reg_train, reg_train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_reg_test, reg_test_pred))

    # =========================
    # CLASSIFICATION METRICS
    # =========================

    train_cls_acc = accuracy_score(y_cls_train, cls_train_pred)
    test_cls_acc = accuracy_score(y_cls_test, cls_test_pred)

    precision = precision_score(
        y_cls_test,
        cls_test_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_cls_test,
        cls_test_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_cls_test,
        cls_test_pred,
        average="weighted",
        zero_division=0
    )

    labels = ["Low", "Medium", "High"]

    cm = confusion_matrix(
        y_cls_test,
        cls_test_pred,
        labels=labels
    )

    report = classification_report(
        y_cls_test,
        cls_test_pred,
        labels=labels,
        zero_division=0
    )

    # =========================
    # SAVE MODELS
    # =========================

    REG_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(REG_MODEL_FILE, "wb") as f:
        pickle.dump(regression_model, f)

    with open(CLS_MODEL_FILE, "wb") as f:
        pickle.dump(classification_model, f)

    # =========================
    # METRICS REPORT
    # =========================

    metrics_text = f"""
SMART RETAIL SALES MODEL REPORT

Dataset:
Total Rows: {df.shape[0]}
Total Columns: {df.shape[1]}

Train/Test Split:
Training Rows: {len(train_idx)} ({len(train_idx) / len(df) * 100:.2f}%)
Testing Rows: {len(test_idx)} ({len(test_idx) / len(df) * 100:.2f}%)

Regression Model:
Model Used: ExtraTreesRegressor with log target transformation
Training Accuracy / R2: {train_r2 * 100:.2f}%
Testing Accuracy / R2: {test_r2 * 100:.2f}%
Train MAE: {train_mae:.2f}
Test MAE: {test_mae:.2f}
Train RMSE: {train_rmse:.2f}
Test RMSE: {test_rmse:.2f}
R2 Gap: {abs(train_r2 - test_r2) * 100:.2f}%

Classification Model:
Model Used: RandomForestClassifier
Training Classification Accuracy: {train_cls_acc * 100:.2f}%
Testing Classification Accuracy: {test_cls_acc * 100:.2f}%
Classification Accuracy Gap: {abs(train_cls_acc - test_cls_acc) * 100:.2f}%

Testing Precision: {precision * 100:.2f}%
Testing Recall: {recall * 100:.2f}%
Testing F1 Score: {f1 * 100:.2f}%

Regression Configuration Used:
- ExtraTreesRegressor used for sales value prediction
- Log target transformation used for skewed retail sales values
- Product-level and transaction-level features used
- Model depth and leaf size controlled for better generalization

Classification Configuration Used:
- RandomForestClassifier used for Low, Medium, High sales class prediction
- Separate classification feature set used
- Train-test split evaluation used for generalization check
- Precision, recall, F1-score and confusion matrix used for evaluation
Confusion Matrix:
Labels: {labels}
{cm}

Classification Report:
{report}

Saved Models:
Regression Model: {REG_MODEL_FILE}
Classification Model: {CLS_MODEL_FILE}
Metrics File: {METRICS_FILE}
"""

    METRICS_FILE.write_text(metrics_text, encoding="utf-8")

    print(metrics_text)


if __name__ == "__main__":
    main()