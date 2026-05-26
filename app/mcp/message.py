from pydantic import BaseModel
from typing import Dict, Any

class MCPMessage(BaseModel):
    sender: str
    receiver: str
    query: str
    context: Dict[str, Any] = {}