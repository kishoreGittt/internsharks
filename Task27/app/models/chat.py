from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    conversation_id: str | None = None

    message: str = Field(
        min_length=1,
        max_length=5000
    )

    document_ids: list[str] = []


class ChatSource(BaseModel):

    document_id: str

    chunk_id: str

    score: float


class ChatResponse(BaseModel):

    success: bool

    status_code: int

    conversation_id: str

    answer: str

    sources: list[ChatSource] = []

    tool_calls: list[dict] = []

    trace_id: str