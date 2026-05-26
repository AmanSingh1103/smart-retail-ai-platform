import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter

from app.utils.logger import logger


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

router = APIRouter(prefix="/azure", tags=["Azure Key Vault"])


@router.get("/keyvault-status")
def keyvault_status():
    """
    Shows Key Vault/security configuration without exposing secret values.
    """

    logger.info("Azure Key Vault status API called")

    return {
        "service": "Azure Key Vault",
        "status": "checked",
        "message": "Secret availability checked without exposing values",
        "key_vault": {
            "vault_name": "smart-retail-key",
            "vault_url": os.getenv("KEY_VAULT_URL"),
            "use_key_vault": os.getenv("USE_KEY_VAULT", "false")
        },
        "environment_variables_available": {
            "azure_openai_api_key": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "azure_openai_endpoint": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
            "azure_openai_deployment": bool(os.getenv("AZURE_OPENAI_DEPLOYMENT")),
            "azure_search_endpoint": bool(os.getenv("AZURE_SEARCH_ENDPOINT")),
            "azure_search_admin_key": bool(os.getenv("AZURE_SEARCH_ADMIN_KEY") or os.getenv("AZURE_SEARCH_KEY")),
            "azure_search_index_name": bool(os.getenv("AZURE_SEARCH_INDEX_NAME")),
            "mongo_uri": bool(os.getenv("MONGO_URI"))
        },
        "security_note": (
            "Secrets are not hardcoded in source code. "
            "Local development uses environment variables. "
            "Azure Key Vault is created for production secret storage."
        )
    }