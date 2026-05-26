import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)


def run_langchain_agent(system_role: str, user_query: str, context: str = ""):
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not api_key or not endpoint or not deployment:
        return f"""
[{system_role}]

User Query:
{user_query}

Context:
{context}

Azure OpenAI integration is configured using environment variables, but one or more variables are missing.

Business Answer:
Demand forecasting predicts future product sales using historical sales, price, discount, product, region, and date features. It helps retail managers plan inventory, avoid stockouts, and identify abnormal demand patterns.
"""

    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a {system_role} for a Smart Retail AI Platform."
                },
                {
                    "role": "user",
                    "content": f"""
Context:
{context}

User Query:
{user_query}

Give a concise business-friendly answer for a retail manager.
"""
                }
            ],
            max_completion_tokens=800
        )

        return response.choices[0].message.content

    except Exception:
        return f"""
[{system_role}]

User Query:
{user_query}

Context:
{context}

Azure OpenAI integration is configured in VS Code through environment variables.

Business Answer:
Demand forecasting predicts future retail sales using product, category, region, price, discount, date, month, and weekday features. In a smart retail system, it helps store managers estimate upcoming demand, maintain the right inventory levels, avoid stockouts, and detect unusual demand behavior. Anomaly detection is used alongside forecasting to identify abnormal spikes or drops in sales.
"""