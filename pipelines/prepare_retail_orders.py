import pandas as pd
from pathlib import Path

RAW_FILE = Path("data/raw/retail_orders.csv")
PROCESSED_FILE = Path("data/processed/retail_orders_clean.csv")


def main():
    df = pd.read_csv(RAW_FILE)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=True)
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce", dayfirst=True)

    numeric_cols = ["sales", "quantity", "discount", "profit", "shipping_cost"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["ship_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["order_month"] = df["order_date"].dt.month
    df["order_year"] = df["order_date"].dt.year
    df["profit_margin"] = df["profit"] / (df["sales"] + 1)

    df["sales_class"] = df["sales"].apply(
        lambda x: "Low" if x < 100 else ("Medium" if x < 500 else "High")
    )

    df = df.dropna(
        subset=[
            "order_date",
            "ship_date",
            "sales",
            "quantity",
            "discount",
            "profit",
            "shipping_cost",
            "ship_days",
            "order_month",
            "order_year",
            "sales_class",
        ]
    )

    keep_columns = [
        "order_id",
        "order_date",
        "ship_date",
        "ship_mode",
        "customer_name",
        "segment",
        "state",
        "country",
        "market",
        "region",
        "product_id",
        "category",
        "sub_category",
        "product_name",
        "sales",
        "quantity",
        "discount",
        "profit",
        "shipping_cost",
        "order_priority",
        "year",
        "ship_days",
        "order_month",
        "order_year",
        "profit_margin",
        "sales_class",
    ]

    df = df[keep_columns]

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)

    print("CLEAN DATASET CREATED SUCCESSFULLY")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print(df.head())


if __name__ == "__main__":
    main()