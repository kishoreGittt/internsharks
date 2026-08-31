import json
import logging

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models.summarizer import AIResult
from app.prompts.summarizer_prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
)


logger = logging.getLogger(__name__)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def summarize_text(
    text: str,
    summary_type: str
) -> AIResult:

    user_prompt = build_user_prompt(
        text=text,
        summary_type=summary_type
    )

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Task 14 AI Summarization API",
    }

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )

    except httpx.TimeoutException:

        logger.error("OpenRouter request timed out")

        raise HTTPException(
            status_code=504,
            detail={
                "success": False,
                "status_code": 504,
                "error": "AI_TIMEOUT",
                "message": "The AI service took too long to respond."
            }
        )

    except httpx.RequestError:

        logger.exception("OpenRouter connection failed")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": "The AI service is currently unavailable."
            }
        )

    # -----------------------------
    # OpenRouter Error Handling
    # -----------------------------

    if response.status_code == 401:

        logger.error("OpenRouter authentication failed")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_AUTHENTICATION_ERROR",
                "message": "Unable to authenticate with the AI service."
            }
        )

    if response.status_code == 429:

        logger.warning("OpenRouter rate limit reached")

        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "status_code": 429,
                "error": "AI_RATE_LIMIT",
                "message": "The AI service rate limit has been reached. Please try again later."
            }
        )

    if response.status_code == 404:

        logger.error("OpenRouter model unavailable")

        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "status_code": 503,
                "error": "MODEL_UNAVAILABLE",
                "message": "The configured AI model is currently unavailable."
            }
        )

    if response.status_code >= 500:

        logger.error(
            "OpenRouter server error: %s",
            response.status_code
        )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_ERROR",
                "message": "The AI service encountered an error."
            }
        )

    if not response.is_success:

        logger.error(
            "Unexpected OpenRouter status: %s",
            response.status_code
        )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_ERROR",
                "message": "Unable to process the summarization request."
            }
        )

    # -----------------------------
    # Parse OpenRouter response
    # -----------------------------

    try:

        response_data = response.json()

        choices = response_data.get("choices")

        if not choices:
            raise ValueError("Missing choices in AI response")

        message = choices[0].get("message")

        if not message:
            raise ValueError("Missing message in AI response")

        content = message.get("content")

        if not content:
            raise ValueError("Missing AI content")

    except (ValueError, TypeError, json.JSONDecodeError):

        logger.exception("Invalid response received from OpenRouter")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "The AI service returned an invalid response."
            }
        )

    # -----------------------------
    # Parse AI JSON
    # -----------------------------

    try:

        if isinstance(content, str):
            ai_json = json.loads(content)
        else:
            ai_json = content

    except (json.JSONDecodeError, TypeError):

        logger.error("AI response was not valid JSON")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_OUTPUT",
                "message": "The AI returned an invalid structured response."
            }
        )

    # -----------------------------
    # Pydantic validation
    # -----------------------------

    try:

        result = AIResult.model_validate(ai_json)

    except Exception:

        logger.exception("AI response failed Pydantic validation")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_OUTPUT",
                "message": "The AI response did not match the required format."
            }
        )

    return result