import pandas as pd
from pathlib import Path

from app.services.langchain_service import run_langchain_agent


DATA_FILE = Path("data/processed/retail_orders_clean.csv")
METRICS_FILE = Path("ml/model_metrics.txt")


def ml_expert_agent(user_query: str):
    try:
        df = pd.read_csv(DATA_FILE)

        total_records = len(df)
        total_sales = round(df["sales"].sum(), 2)
        avg_sales = round(df["sales"].mean(), 2)

        top_category = (
            df.groupby("category")["sales"]
            .sum()
            .sort_values(ascending=False)
            .idxmax()
        )

        top_region = (
            df.groupby("region")["sales"]
            .sum()
            .sort_values(ascending=False)
            .idxmax()
        )

        model_summary = "Model metrics available in ml/model_metrics.txt"

        if METRICS_FILE.exists():
            text = METRICS_FILE.read_text(encoding="utf-8")
            model_summary = "\n".join(text.splitlines()[:18])

        context = f"""
Total Records: {total_records}
Total Sales: {total_sales}
Average Sales: {avg_sales}
Top Category by Sales: {top_category}
Top Region by Sales: {top_region}

Model Summary:
{model_summary}
"""

        response = run_langchain_agent(
            system_role="ML Expert Agent",
            user_query=user_query,
            context=context
        )

        return response

    except Exception as e:
        return f"""
[ML Expert Agent]

User Query:
{user_query}

Error:
{str(e)}

Fallback:
Demand forecasting predicts future retail sales using historical sales, quantity, discount, profit, shipping cost, category, region, and time-based features.
"""