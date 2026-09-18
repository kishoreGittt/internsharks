from pydantic import BaseModel


class JobResponse(BaseModel):

    success: bool

    status_code: int

    job_id: str

    document_id: str

    status: str

    progress: int

    error: str | None = None