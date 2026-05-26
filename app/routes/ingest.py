from fastapi import APIRouter
from app.database.db import db

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/sales")
def ingest_sales(data: dict):
    try:
        result = db.sales.insert_one(data)
        return {"message": "Data inserted", "id": str(result.inserted_id)}
    except Exception as e:
        return {"error": str(e)}