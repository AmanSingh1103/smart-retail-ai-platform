from pydantic import BaseModel


class SalesData(BaseModel):
    order_id: str
    ship_mode: str
    customer_name: str
    segment: str
    state: str
    country: str
    market: str
    region: str
    product_id: str
    category: str
    sub_category: str
    product_name: str
    sales: float
    quantity: int
    discount: float
    profit: float
    shipping_cost: float
    order_priority: str
    year: int
    ship_days: int
    order_month: int
    order_year: int
    profit_margin: float
    sales_class: str


class PredictionInput(BaseModel):
    product_id: str
    ship_mode: str
    segment: str
    state: str
    country: str
    market: str
    region: str
    category: str
    sub_category: str
    order_priority: str
    quantity: int
    discount: float
    profit: float
    shipping_cost: float
    ship_days: int
    order_month: int
    order_year: int
    profit_margin: float


class AgentQuery(BaseModel):
    message: str