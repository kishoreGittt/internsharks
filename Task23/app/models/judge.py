from pydantic import BaseModel, Field

class JudgeResponse(BaseModel):
    relevance: float = Field(ge=0, le=1)
    groundedness: float = Field(ge=0, le=1)
    correctness: float = Field(ge=0, le=1)
    reason: str = ""
