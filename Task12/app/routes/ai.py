from fastapi import APIRouter, HTTPException, status

from app.models.ai import AIRequest

from app.services.ai_service import (
    ai_service,
    AIRateLimitError,
    AIAuthenticationError,
    AIServiceUnavailableError
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/generate")
async def generate_ai_response(request: AIRequest):

    try:

        response = await ai_service.generate_response(
            request.prompt
        )

        return {
            "success": True,
            "status_code": 200,
            "response": response
        }

    except AIRateLimitError:

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "success": False,
                "status_code": 429,
                "error": "AI_RATE_LIMIT_EXCEEDED",
                "message": "AI rate limit exceeded. Please try again later"
            }
        )

    except AIAuthenticationError:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "status_code": 503,
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": "AI service is currently unavailable"
            }
        )

    except AIServiceUnavailableError:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "status_code": 503,
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": "AI service is currently unavailable"
            }
        )