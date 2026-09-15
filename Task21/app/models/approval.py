from pydantic import BaseModel


class ApprovalRequest(BaseModel):
    approved: bool