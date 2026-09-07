from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    goal: str = Field(
        ...,
        min_length=1,
        description="High-level goal for the AI agent"
    )


class ExecutionStep(BaseModel):
    step: int
    tool: str
    arguments: Dict[str, Any]
    result: Any
    status: str


class AgentRunData(BaseModel):
    run_id: str
    goal: str
    status: str
    steps_executed: int
    tools_used: List[str]
    response: str


class AgentRunResponse(BaseModel):
    success: bool
    status_code: int
    data: AgentRunData


class ExecutionTraceResponse(BaseModel):
    success: bool
    status_code: int
    data: Dict[str, Any]