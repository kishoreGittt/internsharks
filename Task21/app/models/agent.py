from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentRunCreate(BaseModel):
    goal: str = Field(..., min_length=1)


class PendingAction(BaseModel):
    action_id: str
    tool: str
    arguments: dict[str, Any]


class AgentRunResponse(BaseModel):
    run_id: str
    goal: str
    status: str
    step_count: int
    pending_action: Optional[dict[str, Any]] = None


class ApprovalRequest(BaseModel):
    approved: bool