from typing import Optional

from fastapi import APIRouter, HTTPException

from app.database.db import db
from app.utils.logger import logger

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/sales")
def search_sales(
    category: Optional[str] = None,
    region: Optional[str] = None,
    product_name: Optional[str] = None,
    limit: int = 10
):
    try:
        logger.info("Search API called")

        query = {}

        if category:
            query["category"] = category

        if region:
            query["region"] = region

        if product_name:
            query["product_name"] = {"$regex": product_name, "$options": "i"}

        results = list(
            db.sales.find(query, {"_id": 0}).limit(limit)
        )

        logger.info(f"Search completed. Records found: {len(results)}")

        return {
            "query": query,
            "count": len(results),
            "data": results
        }

    except Exception as e:
        logger.error(f"Search API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))