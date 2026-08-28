from fastapi import APIRouter

from app.models.ai import AIAnalyzeRequest
from app.services.ai_service import analyze_text


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/analyze")
async def analyze_ai(request: AIAnalyzeRequest):

    result = await analyze_text(request.text)

    return {
        "success": True,
        "status_code": 200,
        "data": result.model_dump()
    }