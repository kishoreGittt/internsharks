import json
import logging

import httpx
from fastapi import HTTPException

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_URL,
)

from app.models.ai import AIAnalysisResponse
from app.prompts.analysis_prompt import ANALYSIS_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


async def analyze_text(text: str) -> AIAnalysisResponse:

    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key is not configured")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "AI_CONFIGURATION_ERROR",
                "message": "AI service is not configured"
            }
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": ANALYSIS_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        "temperature": 0.2,
    }

    try:

        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
            )

    except httpx.TimeoutException:

        logger.error("OpenRouter request timed out")

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

        logger.exception("OpenRouter connection error")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_ERROR",
                "message": "Unable to connect to AI service"
            }
        )

    # Invalid API key
    if response.status_code in (401, 403):

        logger.error(
            "OpenRouter authentication failed: %s",
            response.status_code
        )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_AUTHENTICATION_ERROR",
                "message": "AI service authentication failed"
            }
        )

    # Rate limit
    if response.status_code == 429:

        logger.warning("OpenRouter rate limit reached")

        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "status_code": 429,
                "error": "AI_RATE_LIMIT",
                "message": "AI service rate limit exceeded"
            }
        )

    # Other OpenRouter errors
    if response.status_code >= 400:

        logger.error(
            "OpenRouter API returned status %s",
            response.status_code
        )

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

        logger.error("OpenRouter returned invalid JSON")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI returned an invalid response format"
            }
        )

    # Extract AI content
    try:
        choices = result.get("choices")

        if not choices:
            raise ValueError("Missing choices")

        message = choices[0].get("message")

        if not message:
            raise ValueError("Missing message")

        ai_content = message.get("content")

        if not ai_content:
            raise ValueError("Empty AI response")

    except (AttributeError, IndexError, TypeError, ValueError):

        logger.error("Unexpected AI response structure")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI returned an invalid response format"
            }
        )

    # Convert AI text to JSON
    try:

        cleaned_content = ai_content.strip()

        # Remove accidental markdown code fences
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]

        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]

        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        cleaned_content = cleaned_content.strip()

        parsed_data = json.loads(cleaned_content)

    except (json.JSONDecodeError, TypeError):

        logger.error("AI returned invalid JSON")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI returned an invalid response format"
            }
        )

    # Pydantic validation
    try:

        validated_data = AIAnalysisResponse.model_validate(
            parsed_data
        )

        return validated_data

    except Exception:

        logger.error("AI output failed Pydantic validation")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_AI_RESPONSE",
                "message": "AI returned an invalid response format"
            }
        )