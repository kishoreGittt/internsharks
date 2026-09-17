
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_IMAGE_MODEL,
    OPENROUTER_TIMEOUT_SECONDS,
)
from app.models.vision import ImageGenerationResponse


async def generate_image(
    prompt: str,
) -> ImageGenerationResponse:

    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "MISSING_API_KEY",
                "message": "OPENROUTER_API_KEY is not configured.",
            },
        )

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "EMPTY_PROMPT",
                "message": "Image generation prompt is required.",
            },
        )

    payload: dict[str, Any] = {
        "model": OPENROUTER_IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        async with httpx.AsyncClient(
            timeout=OPENROUTER_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": (
                        f"Bearer {OPENROUTER_API_KEY}"
                    ),
                    "Content-Type": "application/json",
                },
                json=payload,
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={
                "success": False,
                "status_code": 504,
                "error": "OPENROUTER_TIMEOUT",
                "message": "Image generation request timed out.",
            },
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "OPENROUTER_CONNECTION_ERROR",
                "message": str(exc),
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "IMAGE_MODEL_ERROR",
                "message": response.text[:300],
            },
        )

    try:
        response_json = response.json()
        images = extract_images(response_json)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "INVALID_IMAGE_MODEL_RESPONSE",
                "message": str(exc),
            },
        ) from exc

    return ImageGenerationResponse(
        success=True,
        status_code=200,
        model=OPENROUTER_IMAGE_MODEL,
        prompt=prompt,
        images=images,
        raw_response=response_json,
    )


def extract_images(
    response_json: dict[str, Any],
) -> list[str]:

    images: list[str] = []

    choices = response_json.get("choices", [])

    for choice in choices:
        message = choice.get("message", {})

        message_images = message.get("images", [])

        if isinstance(message_images, list):
            for item in message_images:
                if isinstance(item, str):
                    images.append(item)

                elif isinstance(item, dict):
                    image_url = item.get("image_url", {})
                    url = image_url.get("url")

                    if isinstance(url, str):
                        images.append(url)

                    elif isinstance(item.get("url"), str):
                        images.append(item["url"])

        content = message.get("content")

        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue

                if item.get("type") in {
                    "image_url",
                    "output_image",
                }:
                    image_url = item.get("image_url", {})
                    url = image_url.get("url")

                    if isinstance(url, str):
                        images.append(url)

                    elif isinstance(item.get("url"), str):
                        images.append(item["url"])

    if not images:
        raise ValueError(
            "The image model did not return a recognized image result."
        )

    return images