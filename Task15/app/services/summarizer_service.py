import json

import httpx
from fastapi import HTTPException

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    MODEL_NAME
)

from app.models.summarizer import AIResponse

from app.prompts.summarizer_prompt import (
    create_summarization_prompt
)


VALID_SUMMARY_TYPES = {
    "brief",
    "detailed",
    "bullet_points"
}


async def summarize_text(
    text: str,
    summary_type: str
) -> AIResponse:

    # Validate summary type
    if summary_type not in VALID_SUMMARY_TYPES:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SUMMARY_TYPE",
                "message": (
                    "Summary type must be "
                    "brief, detailed, or bullet_points"
                )
            }
        )

    # Validate text
    if not text or not text.strip():

        raise HTTPException(
            status_code=400,
            detail={
                "error": "EMPTY_TEXT",
                "message": "Text cannot be empty"
            }
        )

    # Validate API key
    if not OPENROUTER_API_KEY:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AI_CONFIGURATION_ERROR",
                "message": "AI service is not configured"
            }
        )

    prompt = create_summarization_prompt(
        text,
        summary_type
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    try:

        async with httpx.AsyncClient(
            timeout=60.0
        ) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload
            )

    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail={
                "error": "AI_TIMEOUT",
                "message": "AI service request timed out"
            }
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI_SERVICE_UNAVAILABLE",
                "message": "AI service is unavailable"
            }
        )

    # Invalid API key
    if response.status_code == 401:

        raise HTTPException(
            status_code=401,
            detail={
                "error": "INVALID_API_KEY",
                "message": "Invalid AI API key"
            }
        )

    # Rate limit
    if response.status_code == 429:

        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "AI service rate limit reached"
            }
        )

    # Model unavailable
    if response.status_code == 404:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "MODEL_UNAVAILABLE",
                "message": "AI model is unavailable"
            }
        )

    # Other AI server errors
    if response.status_code >= 500:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI_SERVICE_FAILURE",
                "message": "AI service failure"
            }
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI_REQUEST_FAILED",
                "message": "AI request failed"
            }
        )

    # Read AI response
    try:

        response_data = response.json()

        ai_content = (
            response_data["choices"][0]
            ["message"]["content"]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ):

        raise HTTPException(
            status_code=502,
            detail={
                "error": "INVALID_AI_RESPONSE",
                "message": "Invalid response received from AI service"
            }
        )

    # Validate structured AI output
    try:

        ai_content = ai_content.strip()

        # Remove accidental Markdown code block
        if ai_content.startswith("```json"):

            ai_content = ai_content[7:]

        elif ai_content.startswith("```"):

            ai_content = ai_content[3:]

        if ai_content.endswith("```"):

            ai_content = ai_content[:-3]

        ai_content = ai_content.strip()

        parsed_data = json.loads(ai_content)

        validated_response = AIResponse.model_validate(
            parsed_data
        )

        return validated_response

    except Exception:

        raise HTTPException(
            status_code=502,
            detail={
                "error": "INVALID_AI_OUTPUT",
                "message": "AI returned an invalid response"
            }
        )