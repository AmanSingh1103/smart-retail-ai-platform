from fastapi import APIRouter

router = APIRouter(prefix="/pipeline", tags=["Data Engineering Pipeline"])


@router.get("/status")
def pipeline_status():
    return {
        "section": "E. Data Engineering Pipeline",
        "status": "Completed",
        "tools_used": [
            "Azure Data Factory",
            "Azure Databricks",
            "PySpark",
            "Spark SQL",
            "Azure Blob Storage",
            "Parquet"
        ],
        "flow": "Landing → Raw → Staged → Curated",
        "layers": {
            "landing": "landing/retail_sales.csv",
            "raw": "raw/retail_sales.csv",
            "staged": "staged/retail_sales_staged_parquet",
            "curated": "curated/retail_sales_curated_parquet",
            "sql_analytics": "curated/sql_analytics_parquet"
        },
        "description": "ADF ingests raw data, Databricks PySpark cleans and transforms data, Spark SQL generates analytics, and outputs are saved as parquet."
    }