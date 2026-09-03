from fastapi import APIRouter, HTTPException

from app.models.assistant import AssistantRequest
from app.services.assistant_service import AssistantService


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


assistant_service = AssistantService()


@router.post("/assistant")
def assistant(request: AssistantRequest):

    try:

        result = assistant_service.process_message(
            request.message
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"AI assistant error: {str(exc)}"
        )