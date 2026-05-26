from app.services.langchain_service import run_langchain_agent
from app.mcp.context import shared_context

def data_analyst_agent(message):
    try:
        from app.database.db import db
        sales_data = list(db.sales.find({}, {"_id": 0}))
    except Exception:
        sales_data = []

    if not sales_data:
        context = """
No live MongoDB sales data available.
Using sample retail analytics context:
Total Records: 15
Top Products: Shampoo, Rice, Soap
Purpose: demand forecasting and anomaly detection for smart retail.
"""
    else:
        total_sales = sum(item.get("sales", 0) for item in sales_data)

        context = f"""
Total Records: {len(sales_data)}
Total Sales: {total_sales}
Sample Sales Data: {sales_data[:5]}
"""

    response = run_langchain_agent(
        system_role="Data Analyst Agent",
        user_query=message.query,
        context=context
    )

    shared_context["latest_sales_summary"] = context
    return response