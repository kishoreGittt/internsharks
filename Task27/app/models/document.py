from pydantic import BaseModel


class DocumentResponse(BaseModel):

    success: bool

    status_code: int

    document_id: str

    job_id: str

    status: str