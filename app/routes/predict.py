from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ml.predict import predict_sales
from app.utils.logger import logger


router = APIRouter(prefix="/ml", tags=["ML Prediction"])


class PredictionInput(BaseModel):
    product_id: str = "TEC-PH-10000000"
    ship_mode: str = "Standard Class"
    segment: str = "Consumer"
    state: str = "California"
    country: str = "United States"
    market: str = "US"
    region: str = "West"
    category: str = "Technology"
    sub_category: str = "Phones"
    order_priority: str = "Medium"

    quantity: float = 2
    discount: float = 0.1
    profit: float = 50.0
    shipping_cost: float = 10.0
    ship_days: float = 4
    order_month: float = 5
    order_year: float = 2014
    profit_margin: float = 0.2


@router.post("/predict")
def predict_demand(input_data: PredictionInput):
    try:
        logger.info("ML prediction API called")

        result = predict_sales(**input_data.model_dump())

        return result

    except Exception as e:
        logger.error(f"ML prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))