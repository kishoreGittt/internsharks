from typing import Literal

from pydantic import BaseModel, Field


class SummaryResult(BaseModel):
    summary: str = Field(min_length=1)


class KeyPointsResult(BaseModel):
    key_points: list[str] = Field(min_length=1)


class DocumentAnalysisResult(BaseModel):
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    main_topics: list[str]
    key_points: list[str] = Field(min_length=1)


AnalysisType = Literal[
    "summary",
    "key_points",
    "document_analysis",
]