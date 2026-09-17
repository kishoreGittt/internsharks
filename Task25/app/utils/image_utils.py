import base64
import json
import re


def image_to_data_url(
    image_bytes: bytes,
    content_type: str,
) -> str:
    """
    Convert image bytes into a base64 data URL.
    """

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{content_type};base64,{encoded_image}"
    )


def extract_json_object(
    text: str,
) -> dict:
    """
    Extract a JSON object from the model response.

    Supports:
    - Normal JSON
    - JSON inside markdown code fences
    - Extra text before or after JSON
    """

    if not text:
        raise ValueError(
            "Model returned an empty response"
        )

    cleaned_text = text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned_text,
            flags=re.IGNORECASE,
        )

        cleaned_text = re.sub(
            r"\s*```$",
            "",
            cleaned_text,
        )

    try:
        parsed = json.loads(cleaned_text)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Model response is not a JSON object"
            )

        return parsed

    except json.JSONDecodeError:
        start_index = cleaned_text.find("{")
        end_index = cleaned_text.rfind("}")

        if start_index == -1 or end_index == -1:
            raise ValueError(
                "No JSON object found in model response"
            )

        json_text = cleaned_text[
            start_index : end_index + 1
        ]

        parsed = json.loads(json_text)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Extracted response is not a JSON object"
            )

        return parsed