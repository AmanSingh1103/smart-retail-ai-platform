from app.agents.document_agent import document_assistant_agent
from app.agents.data_analyst_agent import data_analyst_agent
from app.agents.ml_expert_agent import ml_expert_agent
from app.mcp.message import MCPMessage


def orchestrate_agents(query: str):
    query_lower = query.lower()

    if any(word in query_lower for word in ["forecast", "prediction", "demand", "anomaly", "model"]):
        response = ml_expert_agent(query)

        return {
            "selected_agent": "ML Expert Agent",
            "response": response
        }

    elif any(word in query_lower for word in ["sales", "revenue", "top product", "analytics", "data"]):
        message = MCPMessage(
            sender="orchestrator",
            receiver="data_analyst",
            query=query
        )

        response = data_analyst_agent(message)

        return {
            "selected_agent": "Data Analyst Agent",
            "response": response
        }

    else:
        message = MCPMessage(
            sender="orchestrator",
            receiver="document_agent",
            query=query
        )

        response = document_assistant_agent(message)

        return {
            "selected_agent": "Document Assistant Agent",
            "response": response
        }