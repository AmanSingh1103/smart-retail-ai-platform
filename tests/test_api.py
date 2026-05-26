import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Running Successfully"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict():
    response = client.post("/ml/predict", json={
        "ship_mode": "Standard Class",
        "segment": "Consumer",
        "state": "California",
        "country": "United States",
        "market": "US",
        "region": "West",
        "category": "Technology",
        "sub_category": "Phones",
        "order_priority": "Medium",
        "quantity": 2,
        "discount": 0.1,
        "profit": 50.0,
        "shipping_cost": 10.0,
        "ship_days": 4,
        "order_month": 5,
        "order_year": 2014,
        "profit_margin": 0.2
    })

    assert response.status_code == 200
    data = response.json()
    assert "predicted_sales" in data
    assert "predicted_sales_class" in data


def test_agent_chat():
    response = client.post("/agent/chat", json={
        "message": "Explain demand forecasting"
    })

    assert response.status_code == 200
    data = response.json()
    assert "selected_agent" in data
    assert "response" in data


def test_search_sales():
    response = client.get("/search/sales?category=Technology&limit=5")
    assert response.status_code == 200
    assert "count" in response.json()
    assert "data" in response.json()


def test_pipeline_status():
    response = client.get("/pipeline/status")
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"


def test_azure_status():
    response = client.get("/azure/status")
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"