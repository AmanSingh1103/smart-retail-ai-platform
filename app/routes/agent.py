from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentQuery
from app.utils.logger import logger
from app.agents.orchestrator import orchestrate_agents

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/chat")
def agent_chat(query: AgentQuery):
    try:
        logger.info(f"Agent chat triggered: {query.message}")

        result = orchestrate_agents(query.message)

        return result

    except Exception as e:
        logger.error(f"Agent API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))