from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User message"
    )


class CalculatorArguments(BaseModel):
    operation: str
    a: float
    b: float


class GetTaskArguments(BaseModel):
    task_id: int