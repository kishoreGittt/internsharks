from typing import List

from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    text: str
    summary_type: str


class AIResponse(BaseModel):
    summary: str
    main_topic: str
    keywords: List[str]


class SummarizeData(BaseModel):
    summary_type: str
    summary: str
    main_topic: str
    keywords: List[str]


class SummarizeResponse(BaseModel):
    success: bool
    status_code: int
    data: SummarizeData


class DocumentSummarizeData(BaseModel):
    file_name: str
    summary_type: str
    summary: str
    main_topic: str
    keywords: List[str]


class DocumentSummarizeResponse(BaseModel):
    success: bool
    status_code: int
    data: DocumentSummarizeData


class ErrorResponse(BaseModel):
    success: bool
    status_code: int
    error: str
    message: str