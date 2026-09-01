from fastapi import APIRouter, HTTPException

from app.models.chat import (
    ChatHistoryData,
    ChatMessage,
    ChatRequest,
    ChatResponseData
)

from app.services.chat_service import (
    chat_with_ai,
    delete_chat_session,
    get_chat_history
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Chat"]
)


@router.post(
    "/chat",
    response_model=dict
)
async def chat(request: ChatRequest):

    try:

        response = await chat_with_ai(
            session_id=request.session_id,
            user_message=request.message
        )

        response_data = ChatResponseData(
            session_id=request.session_id,
            response=response
        )

        return {
            "success": True,
            "status_code": 200,
            "data": response_data.model_dump()
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.get(
    "/chat/{session_id}/history",
    response_model=dict
)
async def get_history(session_id: str):

    if not session_id.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_SESSION_ID",
                "message": "session_id cannot be empty"
            }
        )

    try:

        history = get_chat_history(session_id)

        messages = [
            ChatMessage(**message)
            for message in history
        ]

        history_data = ChatHistoryData(
            session_id=session_id,
            messages=messages
        )

        return {
            "success": True,
            "status_code": 200,
            "data": history_data.model_dump()
        }

    except ValueError:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error": "SESSION_NOT_FOUND",
                "message": "Chat session not found"
            }
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@router.delete(
    "/chat/{session_id}",
    response_model=dict
)
async def delete_chat(session_id: str):

    if not session_id.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_SESSION_ID",
                "message": "session_id cannot be empty"
            }
        )

    try:

        delete_chat_session(session_id)

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "session_id": session_id,
                "message": "Chat conversation cleared successfully"
            }
        }

    except ValueError:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error": "SESSION_NOT_FOUND",
                "message": "Chat session not found"
            }
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )