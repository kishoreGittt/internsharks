import httpx
from fastapi import HTTPException

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_URL
)


async def generate_chat_response(messages: list[dict]) -> str:

    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "CONFIGURATION_ERROR",
                "message": "OpenRouter API key is not configured"
            }
        )

    if not OPENROUTER_MODEL:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "CONFIGURATION_ERROR",
                "message": "OpenRouter model is not configured"
            }
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={
                "success": False,
                "status_code": 504,
                "error": "AI_TIMEOUT",
                "message": "AI service request timed out"
            }
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "status_code": 503,
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": "Unable to connect to AI service"
            }
        )

    # Invalid API key
    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_AUTHENTICATION_ERROR",
                "message": "OpenRouter authentication failed"
            }
        )

    # Rate limit
    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "status_code": 429,
                "error": "RATE_LIMITED",
                "message": "AI service rate limit reached"
            }
        )

    # Model unavailable
    if response.status_code in (404, 503):
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "status_code": 503,
                "error": "MODEL_UNAVAILABLE",
                "message": "The selected AI model is currently unavailable"
            }
        )

    # Other OpenRouter errors
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_ERROR",
                "message": "AI service request failed"
            }
        )

    try:
        result = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI service returned an invalid response"
            }
        )

    try:
        ai_response = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI service returned an unexpected response"
            }
        )

    if not ai_response or not ai_response.strip():
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "EMPTY_AI_RESPONSE",
                "message": "AI service returned an empty response"
            }
        )

    return ai_response.strip()