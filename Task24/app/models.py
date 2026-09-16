from typing import Any
from pydantic import BaseModel, Field

class AIAskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)

class HealthResponse(BaseModel):
    success: bool
    status_code: int
    data: dict[str, Any]
