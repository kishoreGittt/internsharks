from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AIAnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text that needs to be analyzed"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Text cannot be empty")

        return value


class AIAnalysisResponse(BaseModel):
    summary: str = Field(..., min_length=1)

    category: Literal[
        "task",
        "blocker",
        "update",
        "general"
    ]

    priority: Literal[
        "low",
        "medium",
        "high"
    ]

    sentiment: Literal[
        "positive",
        "neutral",
        "negative"
    ]

    keywords: list[str]