import logging
from typing import Any

import requests

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_TIMEOUT_SECONDS,
)

logger = logging.getLogger("task24.ai_service")


class AIServiceError(Exception):
    def __init__(self, category: str, message: str, status_code: int = 500):
        super().__init__(message)
        self.category = category
        self.message = message
        self.status_code = status_code


def classify_openrouter_error(status_code: int, response_text: str = ""):
    text = response_text.lower()
    if status_code == 401 or status_code == 403:
        return "OPENROUTER_AUTH_ERROR", "OpenRouter authentication failed.", 502
    if status_code == 408:
        return "OPENROUTER_TIMEOUT", "The AI provider timed out.", 504
    if status_code == 429:
        return "OPENROUTER_RATE_LIMIT", "OpenRouter rate limit exceeded.", 429
    if status_code in (400, 404):
        if "model" in text or "model" == text.strip():
            return "MODEL_UNAVAILABLE", "The configured model is unavailable.", 502
        return "MODEL_UNAVAILABLE", "The configured model or request is unavailable.", 502
    if status_code >= 500:
        return "OPENROUTER_SERVER_ERROR", "OpenRouter returned a server error.", 502
    return "INTERNAL_ERROR", "The AI provider request failed.", 502


def call_openrouter(message: str) -> dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise AIServiceError(
            "OPENROUTER_AUTH_ERROR",
            "OpenRouter API key is not configured.",
            500,
        )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:8000",
                "X-Title": "Task24 AI Observability API",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant. Answer clearly."},
                    {"role": "user", "content": message},
                ],
            },
            timeout=OPENROUTER_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise AIServiceError("OPENROUTER_TIMEOUT", "The AI provider timed out.", 504) from exc
    except requests.RequestException as exc:
        logger.error("openrouter_connection_error error_type=%s", type(exc).__name__)
        raise AIServiceError("INTERNAL_ERROR", "Could not connect to the AI provider.", 502) from exc

    if response.status_code != 200:
        category, text, status = classify_openrouter_error(response.status_code, response.text)
        raise AIServiceError(category, text, status)

    try:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("empty content")
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise AIServiceError(
            "INVALID_MODEL_RESPONSE",
            "The AI provider returned an invalid response.",
            502,
        ) from exc

    usage = result.get("usage") or {}
    return {
        "response": content,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "model": result.get("model", OPENROUTER_MODEL),
    }
