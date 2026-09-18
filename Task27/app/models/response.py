from pydantic import BaseModel


class StructuredAIResponse(BaseModel):

    success: bool

    status_code: int

    answer: str

    sources: list[dict] = []

    tool_calls: list[dict] = []


class ErrorResponse(BaseModel):

    success: bool = False

    status_code: int

    error: str

    message: str