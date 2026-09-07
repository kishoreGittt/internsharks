from fastapi import APIRouter, HTTPException

from app.models.assistant import (
    AssistantRequest,
    AssistantResponse
)

from app.services.assistant_service import (
    AssistantService
)

from app.storage.chat_memory import (
    get_history,
    clear_history
)


router = APIRouter(
    prefix="/ai/employee-assistant",
    tags=["Employee Assistant"]
)


@router.post(
    "",
    response_model=AssistantResponse
)
def employee_assistant(
    request: AssistantRequest
):

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        service = AssistantService()

        result = service.run(
            session_id=request.session_id,
            user_message=message
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
            status_code=502,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Assistant error: {str(exc)}"
        )


@router.get("/{session_id}/history")
def assistant_history(
    session_id: str
):

    history = get_history(session_id)

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "session_id": session_id,
            "history": history
        }
    }


@router.delete("/{session_id}")
def delete_session(
    session_id: str
):

    clear_history(session_id)

    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation history deleted."
    }