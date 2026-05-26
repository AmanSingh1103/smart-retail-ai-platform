# E. Data Engineering Pipeline

## Objective
The data engineering pipeline processes smart retail sales data using Azure Data Factory, Azure Databricks, PySpark, Spark SQL, and parquet-based storage.

## Architecture

Retail CSV  
→ Landing Layer  
→ Azure Data Factory  
→ Raw Layer  
→ Azure Databricks PySpark  
→ Staged Layer  
→ Curated Layer  
→ Spark SQL Analytics  

## Azure Components Used

1. Azure Blob Storage
   - Stores landing, raw, staged, and curated data.

2. Azure Data Factory
   - Copies retail_sales.csv from landing container to raw container.

3. Azure Databricks
   - Performs PySpark cleaning, feature engineering, aggregation, and Spark SQL analytics.

## Data Layers

### Landing Layer
Initial uploaded CSV file.

Path:
landing/retail_sales.csv

### Raw Layer
ADF-copied source data.

Path:
raw/retail_sales.csv

### Staged Layer
Cleaned and feature-engineered data.

Features added:
- day
- month
- weekday
- discount_flag

Output:
staged/retail_sales_staged_parquet

### Curated Layer
Aggregated analytics-ready dataset.

Metrics:
- total_sales
- avg_sales
- max_sales
- avg_price
- total_discount

Output:
curated/retail_sales_curated_parquet

### Spark SQL Analytics
Spark SQL is used to calculate product/category-level sales insights.

Output:
curated/sql_analytics_parquet

## Deliverables Completed

- Raw → Staged → Curated data flow
- PySpark cleaning and transformation
- Spark SQL analytics
- Parquet-based storage
- Azure Data Factory ingestion
- Azure Databricks processing