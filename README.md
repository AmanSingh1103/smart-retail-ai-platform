# Azure AI & Cloud Integration

## Azure Components Used

### 1. Azure AI Foundry / Azure OpenAI
- Used for GenAI-compatible architecture
- Azure endpoint and API key configured using environment variables
- LangChain-compatible agent workflow implemented

### 2. Azure Key Vault
- Used to securely store:
  - MongoDB URI
  - Azure OpenAI API key
  - Azure OpenAI endpoint
- RBAC-based access control enabled

### 3. Azure App Service (Deployment Ready)
- FastAPI backend prepared for Azure Web App deployment
- Uvicorn startup configuration supported

---

# Deployment Diagram

User
 |
 v
Azure App Service / Web App
(FastAPI Backend)
 |
 +--> MongoDB Atlas
 |
 +--> ML Models (.pkl)
 |
 +--> RAG + Vector Store
 |
 +--> Azure AI Foundry / Azure OpenAI
 |
 +--> Azure Key Vault

---

# Security Considerations

- Secrets are not hardcoded
- .env used for local development
- Azure Key Vault used for secure credential storage
- Environment variables used for deployment configuration
- RBAC-based secret access control implemented
## E. Data Engineering Pipeline

The project implements a cloud-based data engineering pipeline using Azure Data Factory, Azure Databricks, PySpark, Spark SQL, and Azure Blob Storage.

### Pipeline Flow

Retail CSV → Landing → Azure Data Factory → Raw → Azure Databricks PySpark → Staged → Curated → Spark SQL Analytics

### Implementation

- Azure Data Factory copies `retail_sales.csv` from the landing container to the raw container.
- Azure Databricks reads raw data using PySpark.
- PySpark performs data cleaning and feature engineering.
- Staged and curated outputs are stored in parquet format.
- Spark SQL is used for analytics queries.

### Storage Layers

| Layer | Path |
|---|---|
| Landing | landing/retail_sales.csv |
| Raw | raw/retail_sales.csv |
| Staged | staged/retail_sales_staged_parquet |
| Curated | curated/retail_sales_curated_parquet |
| SQL Analytics | curated/sql_analytics_parquet |

### E Section Status

Completed:
- Azure Data Factory ingestion
- Azure Databricks PySpark transformation
- Spark SQL analytics
- Raw → Staged → Curated pipeline
- Parquet-based storage