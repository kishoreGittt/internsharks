"""
OpenRouter AI service.

This file sends the user's message to OpenRouter
and returns the AI response together with token usage.
"""

import time
from typing import Any, Dict

import requests

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class AIServiceError(Exception):
    """
    Custom exception for AI service errors.
    """

    pass


def generate_ai_response(message: str) -> Dict[str, Any]:
    """
    Send a message to OpenRouter and return the AI response.

    Args:
        message: User's input message.

    Returns:
        Dictionary containing:
        - response
        - model
        - usage
        - duration_ms

    Raises:
        AIServiceError: If the OpenRouter request fails.
    """

    if not OPENROUTER_API_KEY:
        raise AIServiceError(
            "OPENROUTER_API_KEY is not configured."
        )

    if not OPENROUTER_MODEL:
        raise AIServiceError(
            "OPENROUTER_MODEL is not configured."
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Task24 AI Observability API",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
    }

    start_time = time.perf_counter()

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

    except requests.exceptions.Timeout as exc:
        raise AIServiceError(
            "OpenRouter request timed out."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise AIServiceError(
            f"Unable to connect to OpenRouter: {exc}"
        ) from exc

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    if response.status_code != 200:
        try:
            error_data = response.json()
        except ValueError:
            error_data = response.text

        raise AIServiceError(
            f"OpenRouter API error {response.status_code}: "
            f"{error_data}"
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise AIServiceError(
            "OpenRouter returned an invalid JSON response."
        ) from exc

    choices = result.get("choices", [])

    if not choices:
        raise AIServiceError(
            "OpenRouter response does not contain choices."
        )

    first_choice = choices[0]

    message_data = first_choice.get("message", {})

    content = message_data.get("content", "")

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    if not content:
        content = "The AI returned an empty response."

    raw_usage = result.get("usage", {}) or {}

    prompt_tokens = raw_usage.get(
        "prompt_tokens",
        raw_usage.get("input_tokens", 0),
    ) or 0

    completion_tokens = raw_usage.get(
        "completion_tokens",
        raw_usage.get("output_tokens", 0),
    ) or 0

    total_tokens = raw_usage.get(
        "total_tokens",
        prompt_tokens + completion_tokens,
    ) or 0

    usage = {
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": int(total_tokens),
    }

    return {
        "response": content,
        "model": result.get(
            "model",
            OPENROUTER_MODEL,
        ),
        "usage": usage,
        "duration_ms": duration_ms,
    }