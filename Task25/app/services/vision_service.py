from typing import Any

import httpx
from fastapi import HTTPException
from PIL import Image
from io import BytesIO

from app.config import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_OUTPUT_RETRIES,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_TIMEOUT_SECONDS,
    OPENROUTER_VISION_MODEL,
)

from app.models.vision import (
    AnalysisType,
    ComparisonResult,
    ComparisonResponse,
    DifferenceItem,
    ImageMetadata,
    VisionResponse,
    VisionResult,
)

from app.prompts.vision_prompt import (
    VISION_SYSTEM_PROMPT,
    get_mode_prompt,
)

from app.utils.image_utils import (
    extract_json_object,
    image_to_data_url,
)


def get_image_dimensions(
    image_bytes: bytes,
) -> tuple[int | None, int | None]:
    """
    Read image width and height.
    """

    try:
        with Image.open(
            BytesIO(image_bytes)
        ) as image:
            return image.width, image.height

    except Exception:
        return None, None


def create_metadata(
    file_name: str,
    content_type: str,
    image_bytes: bytes,
) -> ImageMetadata:
    width, height = get_image_dimensions(
        image_bytes
    )

    return ImageMetadata(
        file_name=file_name,
        content_type=content_type,
        size_bytes=len(image_bytes),
        width=width,
        height=height,
    )


def check_api_key() -> None:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "OPENROUTER_API_KEY is not configured "
                "in the .env file"
            ),
        )


def validate_image_size(
    image_bytes: bytes,
) -> None:
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                "Image size exceeds the allowed limit "
                f"of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB"
            ),
        )


def extract_model_content(
    response_json: dict[str, Any],
) -> str:
    try:
        choices = response_json["choices"]

        if not choices:
            raise ValueError(
                "OpenRouter returned no choices"
            )

        message = choices[0]["message"]

        content = message.get(
            "content",
            "",
        )

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")

                    if text:
                        text_parts.append(text)

            return "\n".join(text_parts)

        return str(content)

    except Exception as exc:
        raise ValueError(
            f"Unable to extract model response: {exc}"
        ) from exc


async def send_openrouter_request(
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    check_api_key()

    url = (
        f"{OPENROUTER_BASE_URL}"
        "/chat/completions"
    )

    headers = {
        "Authorization": (
            f"Bearer {OPENROUTER_API_KEY}"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_VISION_MODEL,
        "messages": messages,
        "temperature": 0,
    }

    try:
        async with httpx.AsyncClient(
            timeout=OPENROUTER_TIMEOUT_SECONDS
        ) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="OpenRouter authentication failed",
            )

        if response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail=(
                    "OpenRouter rate limit exceeded. "
                    "Please try again later."
                ),
            )

        if response.status_code >= 400:
            error_text = response.text[:1000]

            raise HTTPException(
                status_code=502,
                detail=(
                    "OpenRouter API error: "
                    f"{error_text}"
                ),
            )

        return response.json()

    except HTTPException:
        raise

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="OpenRouter request timed out",
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not connect to OpenRouter: "
                f"{str(exc)}"
            ),
        )


def build_analysis_messages(
    image_bytes: bytes,
    content_type: str,
    prompt: str,
    analysis_type: AnalysisType,
) -> list[dict[str, Any]]:
    image_data_url = image_to_data_url(
        image_bytes=image_bytes,
        content_type=content_type,
    )

    mode_prompt = get_mode_prompt(
        analysis_type
    )

    combined_prompt = f"""
{mode_prompt}

User request:
{prompt}

Return only valid JSON.
"""

    return [
        {
            "role": "system",
            "content": VISION_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": combined_prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url,
                    },
                },
            ],
        },
    ]


async def call_vision_model(
    image_bytes: bytes,
    content_type: str,
    file_name: str,
    prompt: str,
    analysis_type: AnalysisType,
) -> VisionResponse:
    validate_image_size(image_bytes)

    messages = build_analysis_messages(
        image_bytes=image_bytes,
        content_type=content_type,
        prompt=prompt,
        analysis_type=analysis_type,
    )

    last_error: Exception | None = None

    for attempt in range(
        MAX_OUTPUT_RETRIES + 1
    ):
        try:
            response_json = await send_openrouter_request(
                messages
            )

            model_content = extract_model_content(
                response_json
            )

            parsed_json = extract_json_object(
                model_content
            )

            parsed_json["analysis_type"] = (
                analysis_type
            )

            result = VisionResult.model_validate(
                parsed_json
            )

            metadata = create_metadata(
                file_name=file_name,
                content_type=content_type,
                image_bytes=image_bytes,
            )

            return VisionResponse(
                success=True,
                status_code=200,
                data=result,
                metadata=metadata,
            )

        except HTTPException:
            raise

        except Exception as exc:
            last_error = exc

            if attempt >= MAX_OUTPUT_RETRIES:
                break

    raise HTTPException(
        status_code=502,
        detail=(
            "Unable to process the vision model response: "
            f"{str(last_error)}"
        ),
    )


def build_comparison_messages(
    image1_bytes: bytes,
    image1_content_type: str,
    image2_bytes: bytes,
    image2_content_type: str,
    prompt: str,
) -> list[dict[str, Any]]:
    image1_data_url = image_to_data_url(
        image_bytes=image1_bytes,
        content_type=image1_content_type,
    )

    image2_data_url = image_to_data_url(
        image_bytes=image2_bytes,
        content_type=image2_content_type,
    )

    comparison_prompt = f"""
Compare the two images carefully.

User request:
{prompt}

Return only valid JSON in this format:

{{
  "summary": "short comparison summary",
  "differences": [
    {{
      "type": "object, color, position, text, or other",
      "description": "visible difference"
    }}
  ],
  "uncertain_details": []
}}

Do not invent differences that are not visible.
"""

    return [
        {
            "role": "system",
            "content": VISION_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": comparison_prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image1_data_url,
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image2_data_url,
                    },
                },
            ],
        },
    ]


async def compare_images_with_model(
    image1_bytes: bytes,
    image1_content_type: str,
    image1_file_name: str,
    image2_bytes: bytes,
    image2_content_type: str,
    image2_file_name: str,
    prompt: str,
) -> ComparisonResponse:
    validate_image_size(image1_bytes)
    validate_image_size(image2_bytes)

    messages = build_comparison_messages(
        image1_bytes=image1_bytes,
        image1_content_type=image1_content_type,
        image2_bytes=image2_bytes,
        image2_content_type=image2_content_type,
        prompt=prompt,
    )

    response_json = await send_openrouter_request(
        messages
    )

    model_content = extract_model_content(
        response_json
    )

    parsed_json = extract_json_object(
        model_content
    )

    result = ComparisonResult.model_validate(
        parsed_json
    )

    metadata = {
        "image1": create_metadata(
            file_name=image1_file_name,
            content_type=image1_content_type,
            image_bytes=image1_bytes,
        ),
        "image2": create_metadata(
            file_name=image2_file_name,
            content_type=image2_content_type,
            image_bytes=image2_bytes,
        ),
    }

    return ComparisonResponse(
        success=True,
        status_code=200,
        data=result,
        metadata=metadata,
    )