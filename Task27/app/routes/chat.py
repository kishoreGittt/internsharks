import time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.config import settings

from app.auth.dependencies import (
    get_current_user
)

from app.models.chat import (
    ChatRequest,
    ChatResponse
)

from app.services.conversation_service import (
    get_or_create_conversation,
    save_user_message,
    save_assistant_message,
    history
)

from app.services.rag_service import (
    retrieve,
    build_context
)

from app.services.ai_service import (
    chat_with_tools
)

from app.storage.repositories.document_repository import (
    get_document
)

from app.observability.tracing import (
    create_trace,
    add_span,
    finish_trace
)

from app.observability.metrics import (
    approximate_cost
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(
        get_current_user
    )
):

    owner_id = current_user[
        "user_id"
    ]

    trace = create_trace(
        owner_id,
        "chat"
    )

    trace_id = trace[
        "trace_id"
    ]

    try:

        # -------------------------------------------------
        # Conversation
        # -------------------------------------------------

        conversation = await get_or_create_conversation(
            user_id=owner_id,
            conversation_id=request.conversation_id
        )

        conversation_id = conversation[
            "conversation_id"
        ]

        # -------------------------------------------------
        # Validate documents
        # -------------------------------------------------

        for document_id in request.document_ids:

            document = await get_document(
                owner_id,
                document_id
            )

            if not document:

                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "status_code": 404,
                        "error": "DOCUMENT_NOT_FOUND",
                        "message": "Selected document was not found."
                    }
                )

            if document.get(
                "status"
            ) != "ready":

                raise HTTPException(
                    status_code=409,
                    detail={
                        "success": False,
                        "status_code": 409,
                        "error": "DOCUMENT_NOT_READY",
                        "message": "Selected document is not ready."
                    }
                )

        # -------------------------------------------------
        # RAG
        # -------------------------------------------------

        rag_results = []

        embedding_ms = 0

        retrieval_ms = 0

        if request.document_ids:

            rag_data = await retrieve(
                owner_id=owner_id,
                query=request.message,
                document_ids=request.document_ids
            )

            rag_results = rag_data.get(
                "results",
                []
            )

            embedding_ms = rag_data.get(
                "embedding_time_ms",
                0
            )

            retrieval_ms = rag_data.get(
                "retrieval_time_ms",
                0
            )

            add_span(
                trace,
                "embedding",
                embedding_ms
            )

            add_span(
                trace,
                "retrieval",
                retrieval_ms
            )

        context = build_context(
            rag_results
        )

        # -------------------------------------------------
        # Conversation history
        # -------------------------------------------------

        previous_messages = await history(
            user_id=owner_id,
            conversation_id=conversation_id
        )

        # -------------------------------------------------
        # System message
        # -------------------------------------------------

        system_content = (
            "You are a production AI Knowledge and "
            "Operations Copilot.\n\n"

            "You can answer questions using the supplied "
            "document context.\n\n"

            "You can also use project operation tools when "
            "the user asks about projects, members, tasks, "
            "or task status.\n\n"

            "Always respect the authenticated user's "
            "project and document ownership.\n\n"

            "Document context:\n"
            +
            (
                context
                if context
                else
                "NO RELEVANT DOCUMENT INFORMATION FOUND."
            )
        )

        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]

        messages.extend(
            previous_messages
        )

        messages.append(
            {
                "role": "user",
                "content": request.message
            }
        )

        # -------------------------------------------------
        # LLM + tools
        # -------------------------------------------------

        llm_start = time.perf_counter()

        result = await chat_with_tools(
            owner_id=owner_id,
            messages=messages,
            trace=trace
        )

        llm_ms = (
            time.perf_counter()
            - llm_start
        ) * 1000

        add_span(
            trace,
            "llm",
            llm_ms,
            {
                "model": settings.OPENROUTER_MODEL
            }
        )

        # -------------------------------------------------
        # Save conversation
        # -------------------------------------------------

        await save_user_message(
            user_id=owner_id,
            conversation_id=conversation_id,
            content=request.message
        )

        await save_assistant_message(
            user_id=owner_id,
            conversation_id=conversation_id,
            content=result["answer"]
        )

        # -------------------------------------------------
        # Trace
        # -------------------------------------------------

        trace["model"] = (
            settings.OPENROUTER_MODEL
        )

        trace["input_tokens"] = (
            result["input_tokens"]
        )

        trace["output_tokens"] = (
            result["output_tokens"]
        )

        trace["approximate_cost"] = approximate_cost(
            result["input_tokens"],
            result["output_tokens"]
        )

        await finish_trace(
            trace,
            "success"
        )

        # -------------------------------------------------
        # Sources
        # -------------------------------------------------

        sources = [
            {
                "document_id": item["document_id"],
                "chunk_id": item["chunk_id"],
                "score": item["score"]
            }
            for item in rag_results
        ]

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        response_payload = {
            "success": True,
            "status_code": 200,
            "conversation_id": conversation_id,
            "answer": result["answer"],
            "sources": sources,
            "tool_calls": result["tool_calls"],
            "trace_id": trace_id
        }

        return ChatResponse.model_validate(
            response_payload
        )

    except HTTPException:

        await finish_trace(
            trace,
            "failed",
            "HTTP_ERROR"
        )

        raise

    except Exception as error:

        print("\n==========================================")
        print("             CHAT ERROR")
        print("==========================================")
        print(
            f"Error type : {type(error).__name__}"
        )
        print(
            f"Error      : {error}"
        )
        print("==========================================\n")

        await finish_trace(
            trace,
            "failed",
            type(error).__name__
        )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_REQUEST_FAILED",
                "message": "AI request failed safely."
            }
        )