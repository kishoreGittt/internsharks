import base64
import httpx

from app.config import settings


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def analyze_image(
    image_bytes: bytes,
    content_type: str,
    prompt: str
):
    """
    Analyze an uploaded image using an OpenRouter vision model.
    """

    if not image_bytes:
        raise RuntimeError("Image data is empty.")

    if not content_type:
        raise RuntimeError("Image content type is missing.")

    if not prompt or not prompt.strip():
        raise RuntimeError("Vision prompt is empty.")

    # ---------------------------------------------------------
    # Convert image bytes -> base64 data URL
    # ---------------------------------------------------------
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data_url = (
        f"data:{content_type};base64,{image_base64}"
    )

    # ---------------------------------------------------------
    # OpenRouter headers
    # ---------------------------------------------------------
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1:8000",
        "X-Title": "Task 27 AI Knowledge & Operations Copilot",
    }

    # ---------------------------------------------------------
    # Vision request
    # ---------------------------------------------------------
    payload = {
        "model": settings.OPENROUTER_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt.strip(),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
    }

    print("\n==========================================")
    print("             VISION REQUEST")
    print("==========================================")
    print(f"Model : {settings.OPENROUTER_VISION_MODEL}")
    print(f"Type  : {content_type}")
    print("==========================================\n")

    # ---------------------------------------------------------
    # Call OpenRouter
    # ---------------------------------------------------------
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
            )
    except httpx.TimeoutException:
        raise RuntimeError(
            "OpenRouter vision request timed out."
        )
    except httpx.RequestError as error:
        raise RuntimeError(
            f"Could not connect to OpenRouter: {error}"
        )

    # ---------------------------------------------------------
    # Print response for debugging
    # ---------------------------------------------------------
    print("\n==========================================")
    print("           VISION API RESPONSE")
    print("==========================================")
    print(f"HTTP Status : {response.status_code}")
    print(f"Response    : {response.text[:5000]}")
    print("==========================================\n")

    # ---------------------------------------------------------
    # HTTP error
    # ---------------------------------------------------------
    if response.status_code != 200:
        raise RuntimeError(
            "OpenRouter vision request failed: "
            f"HTTP {response.status_code} - "
            f"{response.text[:2000]}"
        )

    # ---------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------
    try:
        response_data = response.json()
    except Exception:
        raise RuntimeError(
            "OpenRouter returned an invalid JSON response."
        )

    # ---------------------------------------------------------
    # Check choices
    # ---------------------------------------------------------
    choices = response_data.get("choices")

    if not isinstance(choices, list) or not choices:
        raise RuntimeError(
            "OpenRouter returned no choices. "
            f"Response: {response_data}"
        )

    first_choice = choices[0]

    if not isinstance(first_choice, dict):
        raise RuntimeError(
            "OpenRouter returned an invalid choice object. "
            f"Response: {response_data}"
        )

    # ---------------------------------------------------------
    # Get message
    # ---------------------------------------------------------
    message = first_choice.get("message")

    if not isinstance(message, dict):
        raise RuntimeError(
            "OpenRouter response does not contain a valid message. "
            f"Response: {response_data}"
        )

    # ---------------------------------------------------------
    # Normal response:
    #
    # message.content = "description..."
    # ---------------------------------------------------------
    content = message.get("content")

    if isinstance(content, str):
        content = content.strip()

        if content:
            return {
                "answer": content,
                "model": response_data.get(
                    "model",
                    settings.OPENROUTER_VISION_MODEL,
                ),
            }

    # ---------------------------------------------------------
    # Some providers can return structured content blocks.
    # ---------------------------------------------------------
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                text_value = item.get("text")

                if isinstance(text_value, str):
                    text_value = text_value.strip()

                    if text_value:
                        text_parts.append(text_value)

        if text_parts:

            return {
                "answer": "\n".join(text_parts),
                "model": response_data.get(
                    "model",
                    settings.OPENROUTER_VISION_MODEL,
                ),
            }

    # ---------------------------------------------------------
    # Provider reasoning fallback
    # ---------------------------------------------------------
    reasoning = message.get("reasoning")

    if isinstance(reasoning, str):
        reasoning = reasoning.strip()

        if reasoning:
            return {
                "answer": reasoning,
                "model": response_data.get(
                    "model",
                    settings.OPENROUTER_VISION_MODEL,
                ),
            }

    # ---------------------------------------------------------
    # Check refusal
    # ---------------------------------------------------------
    refusal = message.get("refusal")

    if isinstance(refusal, str) and refusal.strip():
        raise RuntimeError(
            f"Vision model refused the request: {refusal}"
        )

    # ---------------------------------------------------------
    # Final diagnostic error
    # ---------------------------------------------------------
    raise RuntimeError(
        "OpenRouter returned HTTP 200, but no usable vision "
        "answer was found in the response. "
        f"Full response: {response_data}"
    )