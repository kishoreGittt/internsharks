from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="Prompt to send to the AI model"
    )