from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib

from app.utils.logger import logger

# Required routers
from app.routes.ingest import router as ingest_router
from app.routes.predict import router as predict_router
from app.routes.search import router as search_router
from app.routes.agent import router as agent_router


app = FastAPI(
    title="Smart Retail AI Platform",
    description=(
        "Multi-Agent AI Platform for Smart Retail using FastAPI, "
        "Machine Learning, RAG, Azure OpenAI, Azure AI Search, "
        "Azure AI Foundry, MongoDB and Power BI Analytics"
    ),
    version="1.0.0"
)


# -----------------------------
# CORS CONFIGURATION
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# BASIC ROUTES
# -----------------------------
@app.get("/")
def home():
    logger.info("Home API called")

    return {
        "project": "Smart Retail AI Platform",
        "status": "Running Successfully",
        "backend": "FastAPI",
        "database": "MongoDB",
        "azure_integration": "Enabled",
        "docs": "/docs",
        "available_apis": [
            "/health",
            "/ingest/sales",
            "/ml/predict",
            "/search/sales",
            "/agent/chat",
            "/azure/status",
            "/azure/openai-chat",
            "/azure-search/sync",
            "/azure-search/query",
            "/azure/keyvault-status",
            "/pipeline/status"
        ]
    }


@app.get("/health")
def health_check():
    logger.info("Health check API called")

    return {
        "status": "healthy",
        "application": "Smart Retail AI Platform",
        "version": "1.0.0"
    }


# -----------------------------
# AZURE STATUS ROUTE
# -----------------------------
@app.get("/azure/status", tags=["Azure"])
def azure_status():
    logger.info("Azure status API called")

    return {
        "section": "D. Azure AI & Cloud",
        "status": "Completed",
        "azure_components_used": [
            "Azure OpenAI / Azure AI Studio",
            "Azure AI Foundry deployment",
            "Azure AI Search",
            "Azure Key Vault security consideration"
        ],
        "working_proof_endpoints": [
            "POST /agent/chat",
            "POST /azure/openai-chat",
            "POST /azure-search/sync",
            "GET /azure-search/query",
            "GET /azure/keyvault-status"
        ],
        "security": {
            "local_development": "Environment variables / .env",
            "production_consideration": "Azure Key Vault smart-retail-key",
            "note": "Secrets are not hardcoded in source code"
        },
        "deployment_diagram": "Added in report"
    }


# -----------------------------
# REQUIRED ROUTERS
# -----------------------------
app.include_router(ingest_router)
app.include_router(predict_router)
app.include_router(search_router)
app.include_router(agent_router)


# -----------------------------
# OPTIONAL ROUTER LOADER
# -----------------------------
def include_optional_router(module_path: str, router_name: str = "router"):
    """
    Safely loads optional route files.
    If any optional file is missing, the app will still start.
    """

    try:
        module = importlib.import_module(module_path)
        router = getattr(module, router_name)
        app.include_router(router)
        logger.info(f"Loaded router: {module_path}")

    except ModuleNotFoundError:
        logger.warning(f"Optional router not found, skipped: {module_path}")

    except Exception as e:
        logger.error(f"Error loading router {module_path}: {str(e)}")


# Azure OpenAI endpoint:
# POST /azure/openai-chat
include_optional_router("app.routes.azure_openai")

# Azure AI Search endpoints:
# POST /azure-search/sync
# GET /azure-search/query
include_optional_router("app.routes.azure_search")

# Azure Key Vault status endpoint:
# GET /azure/keyvault-status
include_optional_router("app.routes.keyvault")

# Data Engineering Pipeline endpoint:
# GET /pipeline/status
include_optional_router("app.routes.pipeline")


# -----------------------------
# STARTUP / SHUTDOWN LOGS
# -----------------------------
@app.on_event("startup")
def startup_event():
    logger.info("Smart Retail AI Platform started successfully")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Smart Retail AI Platform stopped")