import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from app.utils.logger import logger


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

router = APIRouter(prefix="/azure-search", tags=["Azure AI Search"])

API_VERSION = "2024-07-01"


def get_search_config():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "retail-knowledge-index")
    key = os.getenv("AZURE_SEARCH_ADMIN_KEY") or os.getenv("AZURE_SEARCH_KEY")

    if not endpoint or not index_name or not key:
        raise ValueError("Azure AI Search configuration missing in .env")

    return endpoint.rstrip("/"), index_name, key


@router.post("/sync")
def sync_retail_knowledge_to_search():
    """
    Creates/updates Azure AI Search index and uploads retail knowledge documents.
    """

    try:
        endpoint, index_name, key = get_search_config()

        headers = {
            "Content-Type": "application/json",
            "api-key": key
        }

        index_schema = {
            "name": index_name,
            "fields": [
                {
                    "name": "id",
                    "type": "Edm.String",
                    "key": True,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "title",
                    "type": "Edm.String",
                    "searchable": True,
                    "retrievable": True
                },
                {
                    "name": "content",
                    "type": "Edm.String",
                    "searchable": True,
                    "retrievable": True
                },
                {
                    "name": "category",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": True,
                    "facetable": True,
                    "retrievable": True
                },
                {
                    "name": "source",
                    "type": "Edm.String",
                    "filterable": True,
                    "retrievable": True
                }
            ]
        }

        create_index_url = f"{endpoint}/indexes/{index_name}?api-version={API_VERSION}"

        index_response = requests.put(
            create_index_url,
            headers=headers,
            json=index_schema,
            timeout=20
        )

        if index_response.status_code not in [200, 201, 204]:
            logger.error(f"Azure Search index sync failed: {index_response.text}")
            raise HTTPException(
                status_code=index_response.status_code,
                detail=index_response.text
            )

        documents = {
            "value": [
                {
                    "@search.action": "upload",
                    "id": "1",
                    "title": "Demand Forecasting",
                    "content": "Demand forecasting predicts future retail sales using historical sales, category, region, discount, seasonality and demand patterns. It helps retailers plan inventory and avoid stockouts.",
                    "category": "Machine Learning",
                    "source": "Smart Retail Knowledge Base"
                },
                {
                    "@search.action": "upload",
                    "id": "2",
                    "title": "Anomaly Detection",
                    "content": "Anomaly detection identifies unusual sales spikes, sudden drops, suspicious discounts and abnormal demand behavior.",
                    "category": "Analytics",
                    "source": "Smart Retail Knowledge Base"
                },
                {
                    "@search.action": "upload",
                    "id": "3",
                    "title": "Inventory Optimization",
                    "content": "Inventory optimization helps store managers maintain the right stock level, reduce stockouts and avoid overstocking.",
                    "category": "Retail Operations",
                    "source": "Smart Retail Knowledge Base"
                },
                {
                    "@search.action": "upload",
                    "id": "4",
                    "title": "Smart Retail AI Assistant",
                    "content": "A Smart Retail AI Assistant combines machine learning, analytics, retrieval search and GenAI agents for retail decision making.",
                    "category": "GenAI",
                    "source": "Smart Retail Knowledge Base"
                }
            ]
        }

        upload_url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={API_VERSION}"

        upload_response = requests.post(
            upload_url,
            headers=headers,
            json=documents,
            timeout=20
        )

        if upload_response.status_code not in [200, 201, 204]:
            logger.error(f"Azure Search upload failed: {upload_response.text}")
            raise HTTPException(
                status_code=upload_response.status_code,
                detail=upload_response.text
            )

        logger.info("Azure AI Search sync completed successfully")

        return {
            "service": "Azure AI Search",
            "operation": "sync",
            "status": "completed",
            "index_name": index_name,
            "index_status_code": index_response.status_code,
            "upload_status_code": upload_response.status_code,
            "documents_uploaded": 4
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Azure AI Search sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
def query_azure_search(
    q: str = Query("demand forecasting inventory stockouts"),
    top: int = Query(3)
):
    """
    Queries Azure AI Search index.
    """

    try:
        endpoint, index_name, key = get_search_config()

        headers = {
            "Content-Type": "application/json",
            "api-key": key
        }

        body = {
            "search": q,
            "top": top
        }

        search_url = f"{endpoint}/indexes/{index_name}/docs/search?api-version={API_VERSION}"

        response = requests.post(
            search_url,
            headers=headers,
            json=body,
            timeout=20
        )

        logger.info(f"Azure AI Search query called: {q}")
        logger.info(f"Azure AI Search status code: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Azure AI Search query failed: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        data = response.json()

        results = []

        for item in data.get("value", []):
            results.append({
                "title": item.get("title"),
                "category": item.get("category"),
                "content": item.get("content"),
                "score": item.get("@search.score")
            })

        return {
            "service": "Azure AI Search",
            "operation": "query",
            "status": "working",
            "status_code": response.status_code,
            "index_name": index_name,
            "query": q,
            "count": len(results),
            "results": results
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Azure AI Search query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))