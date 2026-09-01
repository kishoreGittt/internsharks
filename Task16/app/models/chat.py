from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("session_id cannot be empty")

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("message cannot be empty")

        return value


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatResponseData(BaseModel):
    session_id: str
    response: str


class ChatHistoryData(BaseModel):
    session_id: str
    messages: List[ChatMessage]