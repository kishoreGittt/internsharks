from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AssistantResponseData(BaseModel):
    response: str
    tools_used: list[str]


class AssistantResponse(BaseModel):
    success: bool
    status_code: int
    data: AssistantResponseData