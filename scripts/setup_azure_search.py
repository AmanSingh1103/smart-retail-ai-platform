import os
import requests
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "retail-knowledge-index")
key = os.getenv("AZURE_SEARCH_ADMIN_KEY") or os.getenv("AZURE_SEARCH_KEY")

if not endpoint or not key:
    raise ValueError("Azure Search endpoint or key is missing in .env")

headers = {
    "Content-Type": "application/json",
    "api-key": key
}

api_version = "2024-07-01"

# 1. Create index
index_schema = {
    "name": index_name,
    "fields": [
        {
            "name": "id",
            "type": "Edm.String",
            "key": True,
            "filterable": True
        },
        {
            "name": "title",
            "type": "Edm.String",
            "searchable": True
        },
        {
            "name": "content",
            "type": "Edm.String",
            "searchable": True
        },
        {
            "name": "category",
            "type": "Edm.String",
            "searchable": True,
            "filterable": True,
            "facetable": True
        },
        {
            "name": "source",
            "type": "Edm.String",
            "filterable": True
        }
    ]
}

create_index_url = f"{endpoint}/indexes/{index_name}?api-version={api_version}"

index_response = requests.put(
    create_index_url,
    headers=headers,
    json=index_schema
)

print("Index Status Code:", index_response.status_code)
print(index_response.text[:500])

# 2. Upload retail knowledge documents
documents = {
    "value": [
        {
            "@search.action": "upload",
            "id": "1",
            "title": "Demand Forecasting",
            "content": "Demand forecasting predicts future sales using historical sales, category, region, discount, seasonality and customer demand patterns. It helps retailers plan inventory and avoid stockouts.",
            "category": "Machine Learning",
            "source": "Smart Retail Knowledge Base"
        },
        {
            "@search.action": "upload",
            "id": "2",
            "title": "Anomaly Detection",
            "content": "Anomaly detection identifies unusual sales patterns such as sudden spikes, drops, suspicious discounts, or abnormal product demand. It helps retail managers detect operational issues.",
            "category": "Analytics",
            "source": "Smart Retail Knowledge Base"
        },
        {
            "@search.action": "upload",
            "id": "3",
            "title": "Inventory Optimization",
            "content": "Inventory optimization helps store managers maintain the right stock level. It reduces stockouts, avoids overstocking, and improves customer satisfaction.",
            "category": "Retail Operations",
            "source": "Smart Retail Knowledge Base"
        },
        {
            "@search.action": "upload",
            "id": "4",
            "title": "AI Retail Assistant",
            "content": "A smart retail assistant combines machine learning, analytics, search, and GenAI agents to answer business questions and generate insights for retail decision making.",
            "category": "GenAI",
            "source": "Smart Retail Knowledge Base"
        }
    ]
}

upload_url = f"{endpoint}/indexes/{index_name}/docs/index?api-version={api_version}"

upload_response = requests.post(
    upload_url,
    headers=headers,
    json=documents
)

print("Upload Status Code:", upload_response.status_code)
print(upload_response.text[:500])

# 3. Test search query
search_url = f"{endpoint}/indexes/{index_name}/docs/search?api-version={api_version}"

search_body = {
    "search": "demand forecasting inventory stockouts",
    "top": 3
}

search_response = requests.post(
    search_url,
    headers=headers,
    json=search_body
)

print("Search Status Code:", search_response.status_code)
print(search_response.text[:1000])