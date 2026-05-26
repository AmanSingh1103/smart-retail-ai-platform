import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI

from app.utils.logger import logger


router = APIRouter(prefix="/azure", tags=["Azure OpenAI"])


class AzureChatRequest(BaseModel):
    message: str


def load_openai_env():
    """
    Loads .env fresh from project root every time.
    This avoids old/stale environment values.
    """
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path, override=True)

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    return {
        "env_path": str(env_path),
        "api_key": api_key,
        "endpoint": endpoint,
        "deployment": deployment,
        "api_version": api_version,
        "key_exists": bool(api_key)
    }


@router.get("/openai-config")
def azure_openai_config():
    """
    Debug endpoint.
    It checks which Azure OpenAI config the FastAPI server is reading.
    It does not expose the API key.
    """
    config = load_openai_env()

    return {
        "service": "Azure OpenAI",
        "env_path": config["env_path"],
        "key_exists": config["key_exists"],
        "endpoint": config["endpoint"],
        "deployment": config["deployment"],
        "api_version": config["api_version"]
    }


@router.post("/openai-chat")
def azure_openai_chat(request: AzureChatRequest):
    try:
        config = load_openai_env()

        if not config["api_key"]:
            raise ValueError("AZURE_OPENAI_API_KEY is missing")

        if not config["endpoint"]:
            raise ValueError("AZURE_OPENAI_ENDPOINT is missing")

        if not config["deployment"]:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is missing")

        client = AzureOpenAI(
            api_key=config["api_key"],
            azure_endpoint=config["endpoint"],
            api_version=config["api_version"]
        )

        response = client.chat.completions.create(
            model=config["deployment"],
            messages=[
                {
                    "role": "system",
                    "content": "You are an Azure OpenAI assistant for a Smart Retail AI project."
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            max_completion_tokens=200
        )

        logger.info("Azure OpenAI direct chat endpoint called successfully")

        return {
            "service": "Azure OpenAI",
            "deployment": config["deployment"],
            "status": "working",
            "config_source": "Environment Variables / Key Vault Ready",
            "response": response.choices[0].message.content
        }

    except Exception as e:
        config = load_openai_env()

        logger.error(f"Azure OpenAI direct chat error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "debug_config": {
                    "env_path": config["env_path"],
                    "key_exists": config["key_exists"],
                    "endpoint": config["endpoint"],
                    "deployment": config["deployment"],
                    "api_version": config["api_version"]
                }
            }
        )