from typing import Literal

from pydantic import BaseModel, Field, field_validator


SummaryType = Literal["brief", "detailed", "bullet_points"]


class SummarizeRequest(BaseModel):
    text: str = Field(
        ...,
        description="Text that needs to be summarized"
    )

    summary_type: SummaryType = Field(
        ...,
        description="Type of summary: brief, detailed, or bullet_points"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Text cannot be empty")

        return value


class AIResult(BaseModel):
    summary: str
    main_topic: str
    keywords: list[str]


class SummarizeResponse(BaseModel):
    success: bool
    status_code: int
    data: dict