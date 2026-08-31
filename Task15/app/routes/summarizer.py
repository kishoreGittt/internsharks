from fastapi import APIRouter

from app.models.summarizer import (
    SummarizeRequest,
    SummarizeResponse
)

from app.services.summarizer_service import (
    summarize_text
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Summarization"]
)


@router.post(
    "/summarize",
    response_model=SummarizeResponse
)
async def summarize(request: SummarizeRequest):

    result = await summarize_text(
        request.text,
        request.summary_type
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "summary_type": request.summary_type,
            "summary": result.summary,
            "main_topic": result.main_topic,
            "keywords": result.keywords
        }
    }