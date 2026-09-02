from pydantic import BaseModel, Field


class AskRequest(BaseModel):

    document_id: str = Field(
        ...,
        min_length=1
    )

    question: str = Field(
        ...,
        min_length=1
    )


class DocumentData(BaseModel):

    document_id: str

    file_name: str

    chunks_created: int


class AskData(BaseModel):

    document_id: str

    question: str

    answer: str