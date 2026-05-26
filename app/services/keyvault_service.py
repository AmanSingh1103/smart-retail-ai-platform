import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from app.utils.logger import logger


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)


SECRET_NAME_MAP = {
    "AZURE_OPENAI_API_KEY": "azure-openai-api-key",
    "AZURE_OPENAI_ENDPOINT": "azure-openai-endpoint",
    "AZURE_OPENAI_DEPLOYMENT": "azure-openai-deployment",
    "AZURE_OPENAI_API_VERSION": "azure-openai-api-version",
    "MONGO_URI": "mongo-uri",
    "AZURE_SEARCH_ENDPOINT": "azure-search-endpoint",
    "AZURE_SEARCH_ADMIN_KEY": "azure-search-admin-key",
    "AZURE_SEARCH_INDEX_NAME": "azure-search-index-name",
}


def use_key_vault() -> bool:
    return os.getenv("USE_KEY_VAULT", "false").lower() == "true"


@lru_cache(maxsize=1)
def get_secret_client():
    vault_url = os.getenv("KEY_VAULT_URL")

    if not vault_url:
        return None

    credential = DefaultAzureCredential()

    return SecretClient(
        vault_url=vault_url,
        credential=credential
    )


@lru_cache(maxsize=50)
def get_config_value(env_name: str, default: str = None, required: bool = False):
    """
    Reads configuration in this order:
    1. Azure Key Vault, if USE_KEY_VAULT=true
    2. Environment variable / .env fallback
    3. Default value
    """

    secret_name = SECRET_NAME_MAP.get(env_name)

    if use_key_vault() and secret_name:
        try:
            client = get_secret_client()

            if client:
                secret = client.get_secret(secret_name)
                logger.info(f"Loaded secret from Azure Key Vault: {secret_name}")
                return secret.value

        except Exception as e:
            logger.warning(
                f"Could not load secret '{secret_name}' from Key Vault. "
                f"Falling back to environment variable. Error: {str(e)}"
            )

    env_value = os.getenv(env_name)

    if env_value:
        return env_value

    if required and default is None:
        raise ValueError(f"Missing required configuration: {env_name}")

    return default


def check_keyvault_status():
    """
    Checks whether required secrets are accessible.
    It never returns secret values.
    """

    vault_url = os.getenv("KEY_VAULT_URL")

    status = {
        "key_vault_url": vault_url,
        "use_key_vault": use_key_vault(),
        "configured": bool(vault_url),
        "secrets": {}
    }

    for env_name, secret_name in SECRET_NAME_MAP.items():
        try:
            value = get_config_value(env_name)
            status["secrets"][secret_name] = bool(value)

        except Exception:
            status["secrets"][secret_name] = False

    return status